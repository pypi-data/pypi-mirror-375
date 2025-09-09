import json
from datetime import datetime, timezone


class Event:
    def __init__(self, name: str, data: dict = {}, timestamp: str | None = None):
        self.name = name
        self.data = data
        # Default to current UTC time if not provided
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()


class CustomEvent(Event):
    def __init__(self, name: str, data: dict = {}):
        super().__init__(name, {**data, "custom": True})


class StartEvent(Event):
    def __init__(self):
        super().__init__("start")


class StopEvent(Event):
    def __init__(self):
        super().__init__("stop")


class InterruptEvent(Event):
    def __init__(self):
        super().__init__("interrupt")


class TimeoutEvent(Event):
    def __init__(self, count: int = 0, ms_since_input: int = 0):
        super().__init__("timeout", {"count": count, "ms_since_input": ms_since_input})


class TextEvent(Event):
    def __init__(self, source: str, text: str):
        super().__init__("text", {"source": source, "text": text})


class TextToSpeechEvent(Event):
    def __init__(
        self,
        text: str,
        voice="nova",
        cache=True,
        interruptible: bool = True,
        instructions="",
        speed=1.0,
        stream=None,
    ):
        data = {
            "text": text,
            "voice": voice,
            "cache": cache,
            "interruptible": interruptible,
            "instructions": instructions,
            "speed": speed,
        }

        # Only include stream if explicitly provided (tri-state support)
        if stream is not None:
            data["stream"] = stream

        super().__init__("text_to_speech", data)


class AudioEvent(Event):
    def __init__(self, path: str):
        super().__init__("audio", {"path": path})


class SilenceEvent(Event):
    def __init__(self, duration: int):
        super().__init__("silence", {"duration": duration})


class TransferCallEvent(Event):
    def __init__(self, phone_number: str):
        super().__init__("transfer_call", {"phone_number": phone_number})


class WarmTransferEvent(Event):
    def __init__(self, phone_number: str, data: dict):
        super().__init__("warm_transfer", {"phone_number": phone_number, "data": data})


class MergeCallEvent(Event):
    def __init__(self, call_sid: str):
        super().__init__("merge_call", {"call_sid": call_sid})


class ContextUpdateEvent(Event):
    def __init__(self, context: dict):
        super().__init__("context", {"context": context})


class ErrorEvent(Event):
    def __init__(self, message: str):
        super().__init__("error", {"message": message})


class LogEvent(Event):
    def __init__(self, message: str):
        super().__init__("log", {"message": message})


class CollectPaymentEvent(Event):
    def __init__(self, amount: float):
        super().__init__("collect_payment", {"amount": amount})


class CollectPaymentSuccessEvent(Event):
    def __init__(self):
        super().__init__("collect_payment_success")


class SupervisorRequestEvent(Event):
    def __init__(self, content: str):
        super().__init__("supervisor_request", {"content": content})


class SupervisorResponseEvent(Event):
    def __init__(self, content: str):
        super().__init__("supervisor_response", {"content": content})


class ConnectSTSEvent(Event):
    def __init__(self, configuration: dict):
        super().__init__("connect_sts", {"configuration": configuration})


class DisconnectSTSEvent(Event):
    def __init__(self):
        super().__init__("disconnect_sts", {})


class UpdateCallEvent(Event):
    def __init__(self, data: dict):
        super().__init__("update_call", {"data": data})


class StartRecordingEvent(Event):
    def __init__(self, status_callback_url: str = None):
        super().__init__(
            "start_recording", {"status_callback_url": status_callback_url}
        )


class StopRecordingEvent(Event):
    def __init__(self):
        super().__init__("stop_recording")


class STTUpdateSettingsEvent(Event):
    def __init__(
        self,
        language: str = None,
        prompt: str = None,
        endpointing: int = None,
        noise_reduction_type: str = None,
        model: str = None,
    ):
        super().__init__(
            "stt_update_settings",
            {
                "language": language,
                "prompt": prompt,
                "endpointing": endpointing,
                "noise_reduction_type": noise_reduction_type,
                "model": model,
            },
        )


class STTModelSwitchedEvent(Event):
    def __init__(
        self,
        from_model: str | None,
        to_model: str | None,
        warmup_ms: int = 0,
        switch_delay_ms: int = 0,
    ):
        payload = {
            "from_model": from_model,
            "to_model": to_model,
            "warmup_ms": warmup_ms,
            "switch_delay_ms": switch_delay_ms,
        }
        super().__init__("stt_model_switched", payload)


class TurnEndEvent(Event):
    def __init__(self, duration: int):
        super().__init__("turn_end", {"duration": duration})


class TurnInterruptedEvent(Event):
    def __init__(self):
        super().__init__("turn_interrupted", {})


class InitializeEvent(Event):
    def __init__(
        self, code: str, hash: str, is_multifile: bool, is_debug: bool, context: dict
    ):
        super().__init__(
            "initialize",
            {
                "code": code,
                "hash": hash,
                "is_multifile": is_multifile,
                "is_debug": is_debug,
                "context": context,
            },
        )


class TestingEvent(Event):
    def __init__(self, data: dict):
        super().__init__("testing", {"data": data})


class DebugEvent(Event):
    def __init__(
        self, event_name: str, event_data: dict, direction: str, context: dict
    ):
        super().__init__(
            "debug",
            {
                "event_name": event_name,
                "event_data": event_data,
                "direction": direction,
                "context": context,
            },
        )


class MetricEvent(Event):
    def __init__(self, metric_type: str, name: str, data: dict = {}):
        # metric_type: one of "latency", "count", "gauge", "ratio"
        event_name = f"metrics.{metric_type}.{name}"
        super().__init__(event_name, data or {})


class SessionEndEvent(Event):
    def __init__(self):
        super().__init__("session_end")


class StartSessionEvent(Event):
    def __init__(
        self,
        agent_id: str = "",
        environment: str = "",
        input_type: str = "",
        input_parameters: dict = {},
        parameters: dict = {},
    ):
        super().__init__(
            "start_session",
            {
                "agent_id": agent_id,
                "environment": environment,
                "input_type": input_type,
                "input_parameters": input_parameters,
                "parameters": parameters,
            },
        )


class MergeSessionEvent(Event):
    def __init__(self, session_id: str):
        super().__init__(
            "merge_session",
            {
                "session_id": session_id,
            },
        )


def event_to_str(event: Event) -> str:
    payload = {"name": event.name, "data": event.data, "timestamp": event.timestamp}
    return json.dumps(payload)


def event_from_str(event_str: str) -> Event:
    event = json.loads(event_str)
    name = event["name"]
    # Default timestamp to current UTC if missing
    timestamp = event.get("timestamp") or datetime.now(timezone.utc).isoformat()
    data = event["data"]

    # Dynamic handling for metrics namespace
    if isinstance(name, str) and name.startswith("metrics."):
        try:
            _, metric_type, *metric_name_parts = name.split(".")
            metric_name = ".".join(metric_name_parts) if metric_name_parts else ""
        except Exception:
            metric_type = "unknown"
            metric_name = name
        payload = {k: v for k, v in data.items()}
        return MetricEvent(metric_type, metric_name, payload)

    event_types = {
        "stt_model_switched": lambda: STTModelSwitchedEvent(
            data.get("from_model"),
            data.get("to_model"),
            data.get("warmup_ms", 0),
            data.get("switch_delay_ms", 0),
        ),
        "audio": lambda: AudioEvent(data.get("path")),
        "context": lambda: ContextUpdateEvent(data.get("context")),
        "error": lambda: ErrorEvent(data.get("message")),
        "interrupt": InterruptEvent,
        "log": lambda: LogEvent(data.get("message")),
        "merge_call": lambda: MergeCallEvent(data.get("call_sid")),
        "silence": lambda: SilenceEvent(data.get("duration")),
        "start": StartEvent,
        "stop": StopEvent,
        "text_to_speech": lambda: TextToSpeechEvent(
            data.get("text"),
            data.get("voice", "nova"),
            data.get("cache", True),
            data.get("interruptible", True),
            data.get("instructions", ""),
            data.get("speed", 1.0),
            data.get("stream"),
        ),
        "text": lambda: TextEvent(data.get("source"), data.get("text")),
        "timeout": lambda: TimeoutEvent(data.get("count"), data.get("ms_since_input")),
        "transfer_call": lambda: TransferCallEvent(data.get("phone_number")),
        "warm_transfer": lambda: WarmTransferEvent(
            data.get("phone_number"), data.get("data")
        ),
        "collect_payment": lambda: CollectPaymentEvent(data.get("amount")),
        "collect_payment_success": CollectPaymentSuccessEvent,
        "supervisor_request": lambda: SupervisorRequestEvent(data.get("content")),
        "supervisor_response": lambda: SupervisorResponseEvent(data.get("content")),
        "connect_sts": lambda: ConnectSTSEvent(data.get("configuration")),
        "disconnect_sts": DisconnectSTSEvent,
        "update_call": lambda: UpdateCallEvent(data.get("data")),
        "start_recording": lambda: StartRecordingEvent(data.get("status_callback_url")),
        "stop_recording": StopRecordingEvent,
        "stt_update_settings": lambda: STTUpdateSettingsEvent(
            data.get("language"),
            data.get("prompt"),
            data.get("endpointing"),
            data.get("noise_reduction_type"),
            data.get("model"),
        ),
        "turn_end": lambda: TurnEndEvent(data.get("duration")),
        "turn_interrupted": TurnInterruptedEvent,
        "initialize": lambda: InitializeEvent(
            data.get("code"),
            data.get("hash"),
            data.get("is_multifile"),
            data.get("is_debug"),
            data.get("context"),
        ),
        "debug": lambda: DebugEvent(
            data.get("event_name"),
            data.get("event_data"),
            data.get("direction"),
            data.get("context"),
        ),
        "session_end": SessionEndEvent,
        "testing": lambda: TestingEvent(data.get("data")),
        "start_session": lambda: StartSessionEvent(
            data.get("agent_id"),
            data.get("environment"),
            data.get("input_type"),
            data.get("input_parameters"),
            data.get("parameters"),
        ),
        "merge_session": lambda: MergeSessionEvent(data.get("session_id")),
    }

    if name in event_types:
        e = event_types[name]()
        e.timestamp = timestamp
        return e

    raise ValueError(f"Unknown event type: {name}")


def format_event(event: Event) -> bytes:
    event_string = event_to_str(event)

    return bytes(f"{event_string}\n", "utf-8")
