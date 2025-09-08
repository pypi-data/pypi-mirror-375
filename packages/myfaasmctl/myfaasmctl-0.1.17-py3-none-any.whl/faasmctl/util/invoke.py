from faasmctl.util.batch import (
    serialize_map,
    batch_exec_factory,
    batch_exec_input_factory,
    batch_messages_input_factory,
)
from faasmctl.util.config import (
    get_faasm_ini_file,
    get_faasm_planner_host_port,
)
from faasmctl.util.docker import in_docker
from faasmctl.util.gen_proto.faabric_pb2 import BatchExecuteRequestStatus
from faasmctl.util.message import message_factory
from faasmctl.util.planner import prepare_planner_msg
from google.protobuf.json_format import MessageToDict, MessageToJson, Parse, ParseDict
from requests import post
from time import sleep

import sys
import time


def invoke_wasm(
    msg_dict,
    num_messages=1,
    req_dict=None,
    dict_out=False,
    ini_file=None,
    host_list=None,
    input_list=None,
    chainedId_list=None,
    invoke_period_in=None,
    invoke_retry_in=None,
    poll_period_in=None,
    poll_retry_in=None,
):
    """
    Main entrypoint to invoke an arbitrary message in a Faasm cluster

    Arguments:
    - msg_dict (dict): dict-like object to build a Message Protobuf from
    - num_messages (int): number of said messages to include in the BER
    - req_dict (dict): optional dict-like object to prototype the BER from
    - dict_out (bool): flag to indicate that we expect the result as a JSON
                       instead than as a Message class
    - host_list (array): list of (`num_message`s IPs) where to execute each
                         message. By providing a host list in advance, we
                         are bypassing the planner's scheduling.
                         WARNING: if the host_list breaks the planner's
                         state consistency, the planner will crash, so use
                         this optional argument at your own risk!
    - ini_file (str): path to the cluster's INI file
    - input_list (dict): list of input data for each message
    - chainedId_list (array): list of chainedIds for each message

    Return:
    - The BERStatus result either in a Protobuf class or as a dict if dict_out
      is set
    """
    if req_dict is None:
        req_dict = {"user": msg_dict["user"], "function": msg_dict["function"]}

    req = batch_exec_factory(req_dict, msg_dict, num_messages)
    if input_list is not None:
        assert (
            len(input_list) == num_messages
        ), "Number of input data should match number of messages"
        for i in range(num_messages):
            serialized_input = serialize_map(input_list[i])
            req.messages[i].inputData = bytes(serialized_input)
    if chainedId_list is not None:
        assert (
            len(chainedId_list) == num_messages
        ), "Number of chainedIds should match number of messages"
        for i in range(num_messages):
            req.messages[i].chainedId = chainedId_list[i]

    msg = prepare_planner_msg("EXECUTE_BATCH", MessageToJson(req, indent=None))

    if not ini_file:
        ini_file = get_faasm_ini_file()

    host, port = get_faasm_planner_host_port(ini_file, in_docker())
    url = "http://{}:{}".format(host, port)

    # Work out the number of messages to expect in the result basing on the
    # original message
    expected_num_messages = num_messages
    if "mpi_world_size" in msg_dict:
        expected_num_messages = msg_dict["mpi_world_size"]

    # If provided a host-list, preload the scheduling decision by sending
    # a BER with a rightly-populated messages.executedHost
    if host_list is not None:
        assert len(host_list) == expected_num_messages

        for _ in range(len(req.messages), expected_num_messages):
            req.messages.append(message_factory(msg_dict, req.appId))

        # We preload a scheduling decision by passing a BER with each group
        # index associated to one host in the host list
        for group_idx in range(len(req.messages)):
            req.messages[group_idx].groupIdx = group_idx
            req.messages[group_idx].executedHost = host_list[group_idx]
            group_idx += 1

        preload_msg = prepare_planner_msg(
            "PRELOAD_SCHEDULING_DECISION", MessageToJson(req, indent=None)
        )
        response = post(url, data=preload_msg, timeout=None)
        if response.status_code != 200:
            print(
                "Error preloading scheduling decision (code: {}): {}".format(
                    response.status_code, response.text
                )
            )
            raise RuntimeError("Error preloading scheduling decision!")

    result = invoke_and_await(
        url,
        msg,
        expected_num_messages,
        invoke_period_in=invoke_period_in,
        invoke_retry_in=invoke_retry_in,
        poll_period_in=poll_period_in,
        poll_retry_in=poll_retry_in,
    )

    if dict_out:
        return MessageToDict(result)

    return result


def invoke_and_await(
    url,
    json_msg,
    expected_num_messages,
    invoke_period_in=None,
    invoke_retry_in=None,
    poll_period_in=None,
    poll_retry_in=None,
):
    """
    Invoke the given JSON message to the given URL and poll the planner to
    wait for the response
    """
    poll_period = 2
    if poll_period_in is not None:
        poll_period = poll_period_in
    poll_retry = sys.maxsize
    if poll_retry_in is not None:
        poll_retry = poll_retry_in

    # The first invocation returns an appid to poll for the message. If there
    # are not enough slots, this will POST will fail. In general, we want to
    # tolerate this a number of times (for example, to accomodate for dynamic
    # cluster sizes)

    num_retries = 10
    sleep_period_secs = 0.5

    if invoke_period_in is not None:
        sleep_period_secs = invoke_period_in

    if invoke_retry_in is not None:
        num_retries = invoke_retry_in

    for i in range(num_retries):
        response = post(url, data=json_msg, timeout=None)
        if response.status_code == 500 and response.text == "No available hosts":
            print("No available hosts, retrying... {}/{}".format(i + 1, num_retries))
            sleep(sleep_period_secs)
            continue
        break

    if response.status_code != 200:
        print(
            "POST request failed (code: {}): {}".format(
                response.status_code, response.text
            )
        )

    ber_status = Parse(response.text, BatchExecuteRequestStatus(), True)
    ber_status.expectedNumMessages = expected_num_messages

    json_msg = prepare_planner_msg(
        "EXECUTE_BATCH_STATUS", MessageToJson(ber_status, indent=None)
    )
    for i in range(poll_retry):
        # Sleep at the begining, so that the app is registered as in-flight
        sleep(poll_period)

        response = post(url, data=json_msg, timeout=None)
        if response.status_code != 200:
            # We may query for an app result before it is finished. In this
            # case, by default, the planner endpoint fails. But it is
            # not an error
            if response.text == "App not registered in results":
                pass
            else:
                print(
                    "POST request failed (code: {}): {}".format(
                        response.status_code, response.text
                    )
                )
                break
        else:
            ber_status = Parse(response.text, BatchExecuteRequestStatus(), True)
            if ber_status.finished:
                break

    return ber_status


def invoke_wasm_without_wait(
    app_id,
    msg_dict,
    num_messages=1,
    req_dict=None,
    ini_file=None,
    input_list=None,
    chained_id_list=None,
    num_retries=100,
    sleep_period_secs=1,
):
    """
    Main entrypoint to invoke an arbitrary message in a Faasm cluster

    Arguments:
    - msg_dict (dict): dict-like object to build a Message Protobuf from
    - num_messages (int): number of said messages to include in the BER
    - req_dict (dict): optional dict-like object to prototype the BER from
    - ini_file (str): path to the cluster's INI file

    Return:
    - Invoked AppID
    """
    if req_dict is None:
        req_dict = {"user": msg_dict["user"], "function": msg_dict["function"]}

    req = batch_exec_input_factory(
        req_dict, app_id, msg_dict, num_messages, input_list, chained_id_list
    )

    msg = prepare_planner_msg("EXECUTE_BATCH", MessageToJson(req, indent=None))

    if not ini_file:
        ini_file = get_faasm_ini_file()

    host, port = get_faasm_planner_host_port(ini_file, in_docker())
    url = "http://{}:{}".format(host, port)

    result = False
    result = invoke_without_wait(url, msg, num_retries, sleep_period_secs)

    if result == False:
        return None

    return req.appId


def invoke_without_wait(url, json_msg, num_retries, sleep_period_secs, end_time=None):
    """
    Invoke the given JSON message to the given URL, didn't wait for the result
    """

    for i in range(num_retries):
        now = time.time()
        if (end_time is not None) and (now > end_time):
            print("End time reached, stopping invocation")
            return False
        response = post(url, data=json_msg, timeout=None)
        if response.status_code == 500 and response.text == "No available hosts":
            print("No available hosts, retrying... {}/{}".format(i + 1, num_retries))
            sleep(sleep_period_secs)
            continue
        break

    if response.status_code != 200:
        print(
            "POST request failed (code: {}): {}".format(
                response.status_code, response.text
            )
        )
        return False
    return True


def invoke_by_consumer(json_msg, num_retries, sleep_period_secs, end_time=None):
    ini_file = get_faasm_ini_file()

    host, port = get_faasm_planner_host_port(ini_file, in_docker())
    url = "http://{}:{}".format(host, port)

    for i in range(num_retries):
        # print("Invoking by consumer, attempt {}/{}".format(i + 1, num_retries))
        now = time.time()
        if (end_time is not None) and (now > end_time):
            print("End time reached, stopping invocation")
            return False
        response = post(url, data=json_msg, timeout=None)
        if response.status_code == 500 and response.text == "No available hosts":
            print("No available hosts, retrying... {}/{}".format(i + 1, num_retries))
            sleep(sleep_period_secs)
            continue
        break

    if response.status_code != 200:
        print(
            "POST request failed (code: {}): {}".format(
                response.status_code, response.text
            )
        )
        return False
    return True


def query_result(app_id, poll_period=0.5, url=None, max_retries=0):
    """
    Query the result of an invocation
    """

    if not url:
        ini_file = get_faasm_ini_file()
        host, port = get_faasm_planner_host_port(ini_file, in_docker())
        url = "http://{}:{}".format(host, port)

    try_times = 0
    while True:
        req_dict = {"appId": app_id}
        req = ParseDict(req_dict, BatchExecuteRequestStatus())

        json_msg = prepare_planner_msg(
            "EXECUTE_BATCH_STATUS", MessageToJson(req, indent=None)
        )
        response = post(url, data=json_msg, timeout=None)
        if response.status_code != 200:
            # We may query for an app result before it is finished. In this
            # case, by default, the planner endpoint fails. But it is
            # not an error
            if response.text == "App not registered in results":
                pass
            else:
                print(
                    "POST request failed (code: {}): {}".format(
                        response.status_code, response.text
                    )
                )
                break
        else:
            ber_status = Parse(response.text, BatchExecuteRequestStatus(), True)
            if ber_status.finished:
                break
        sleep(poll_period)
        try_times += 1
        if max_retries > 0 and try_times >= max_retries:
            break

    return ber_status


def invoke_wasm_messages(
    app_id,
    msg_dict,
    num_messages=1,
    req_dict=None,
    ini_file=None,
    input_list=None,
    chained_id_list=None,
    num_retries=100,
    sleep_period_secs=1,
    end_time=None,
):
    """
    Main entrypoint to invoke messages batch in a Faasm cluster

    Arguments:
    - msg_dict (dict): dict-like object to build a Message Protobuf from
    - num_messages (int): number of said messages to include in the BER
    - req_dict (dict): optional dict-like object to prototype the BER from
    - ini_file (str): path to the cluster's INI file

    Return:
    - Invoked AppID
    """
    if req_dict is None:
        req_dict = {"user": msg_dict["user"], "function": msg_dict["function"]}

    req = batch_messages_input_factory(
        req_dict, app_id, msg_dict, num_messages, input_list, chained_id_list
    )

    msg = prepare_planner_msg("EXECUTE_BATCH", MessageToJson(req, indent=None))

    if not ini_file:
        ini_file = get_faasm_ini_file()

    host, port = get_faasm_planner_host_port(ini_file, in_docker())
    url = "http://{}:{}".format(host, port)

    result = False
    result = invoke_without_wait(
        url, msg, num_retries, sleep_period_secs, end_time=end_time
    )

    if result == False:
        return None

    return chained_id_list
