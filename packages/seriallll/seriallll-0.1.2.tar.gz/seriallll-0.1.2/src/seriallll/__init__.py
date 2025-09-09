import time
import threading
import logging
from typing import Optional, Union, Callable
import serial
from serial import SerialException
from serial.tools import list_ports

BytesLike = Union[bytes, bytearray, memoryview]
LineLike = Union[str, bytes]


class SerialClient:
    def __init__(
        self,
        port: Optional[str],
        *,
        baudrate: int = 115200,
        timeout: Optional[float] = 1.0,
        write_timeout: Optional[float] = 1.0,
        max_retries: int = 3,
        retry_delay: float = 0.5,
        backoff_factor: float = 2.0,
        max_retry_delay: float = 10.0,
        auto_reconnect: bool = True,
        on_connect: Optional[Callable[["SerialClient"], None]] = None,
        on_disconnect: Optional[Callable[["SerialClient"], None]] = None,
        on_reconnect: Optional[Callable[["SerialClient"], None]] = None,
        logger: Optional[logging.Logger] = None,
        # passthrough serial kwargs
        bytesize: int = serial.EIGHTBITS,
        parity: str = serial.PARITY_NONE,
        stopbits: float = serial.STOPBITS_ONE,
        xonxoff: bool = False,
        rtscts: bool = False,
        dsrdtr: bool = False,
    ) -> None:
        """
        Notes
        -----
        This constructor does **not** open the port. Call :meth:`connect` to open it.
        The client is thread-safe (uses an internal re-entrant lock) and can
        automatically reconnect on transient I/O failures if `auto_reconnect=True`.

        Parameters
        ----------
        port : Optional[str]
            Serial device path. On macOS typically `/dev/tty.usbserial*` or
            `/dev/tty.usbmodem*`. If ``None``, the port is auto-discovered on
            :meth:`connect` via :meth:`find_first_usb_serial`.
        baudrate : int, default 115200
            Line speed in bits per second.
        timeout : Optional[float], default 1.0
            Read timeout (seconds). ``None`` blocks in the driver.
        write_timeout : Optional[float], default 1.0
            Write timeout (seconds).
        max_retries : int, default 3
            Number of connection attempts (including the first). ``0`` disables
            retry; ``-1`` retries indefinitely.
        retry_delay : float, default 0.5
            Initial delay (seconds) before the first retry.
        backoff_factor : float, default 2.0
            Exponential backoff multiplier applied to the delay between retries.
        max_retry_delay : float, default 10.0
            Upper bound (seconds) for the backoff delay.
        auto_reconnect : bool, default True
            If ``True``, :meth:`read` and :meth:`write` attempt to reopen the port
            when an I/O error occurs or the device is unplugged/replugged.
        on_connect : Optional[Callable[[SerialClient], None]], default None
            Callback invoked after a successful initial connect.
        on_disconnect : Optional[Callable[[SerialClient], None]], default None
            Callback invoked after an explicit :meth:`close` or when the port is
            detected as closed.
        on_reconnect : Optional[Callable[[SerialClient], None]], default None
            Callback invoked after a successful auto-reconnect.
        logger : Optional[logging.Logger], default None
            Logger to use. If ``None``, a basic logger named after the class is
            created at INFO level.

        Other Parameters
        ----------------
        bytesize : int, default ``serial.EIGHTBITS``
            Data bits.
        parity : str, default ``serial.PARITY_NONE``
            Parity mode.
        stopbits : float, default ``serial.STOPBITS_ONE``
            Number of stop bits.
        xonxoff : bool, default False
            Software flow control.
        rtscts : bool, default False
            RTS/CTS hardware flow control.
        dsrdtr : bool, default False
            DSR/DTR hardware flow control.

        Behavior
        --------
        - On (re)connect, DTR is asserted (``setDTR(True)``) which can be required
        by some macOS USB serial adapters/targets.
        - Port discovery on macOS prefers `/dev/tty.usb*` and falls back to
        `/dev/tty.*` if necessary.

        Examples
        --------
        >>> client = SerialClient(port=None, baudrate=115200, max_retries=-1, auto_reconnect=True)
        >>> client.connect()
        >>> client.write_line("hello")
        >>> client.readline(timeout=1.0)
        >>> client.close()
        """
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._write_timeout = write_timeout
        self._max_retries = max(-1, int(max_retries))
        self._retry_delay = float(retry_delay)
        self._backoff_factor = float(backoff_factor)
        self._max_retry_delay = float(max_retry_delay)
        self._auto_reconnect = bool(auto_reconnect)
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_reconnect = on_reconnect
        self._serial_kwargs = dict(
            baudrate=baudrate,
            timeout=timeout,
            write_timeout=write_timeout,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            xonxoff=xonxoff,
            rtscts=rtscts,
            dsrdtr=dsrdtr,
        )

        self._ser: Optional[serial.Serial] = None
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._closing = False

        self.log = logger or logging.getLogger(self.__class__.__name__)
        if not logger:
            handler = logging.StreamHandler()
            fmt = logging.Formatter(
                "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
                datefmt="%H:%M:%S",
            )
            handler.setFormatter(fmt)
            self.log.addHandler(handler)
            self.log.setLevel(logging.INFO)

    @property
    def port(self) -> Optional[str]:
        return self._port

    @property
    def is_open(self) -> bool:
        ser = self._ser
        return bool(ser and ser.is_open)

    def connect(self) -> None:
        """Open the serial port, with optional retries and backoff.
        Raises SerialException if it ultimately fails.
        """
        with self._lock:
            if self.is_open:
                return
            port = self._port or self.find_first_usb_serial()
            if not port:
                raise SerialException(
                    "No serial port specified and none auto-discovered."
                )

            attempt = 0
            delay = max(0.0, self._retry_delay)
            last_exc: Optional[BaseException] = None

            while not self._closing:
                if self._stop_event.is_set():
                    raise SerialException("Connect cancelled")

                attempt += 1
                try:
                    self.log.debug("Opening serial port %s (attempt %d)", port, attempt)
                    ser = serial.Serial(port=port, **self._serial_kwargs)
                    # Ensure DTR is asserted to reset some devices on macOS if needed.
                    ser.setDTR(True)
                    self._ser = ser
                    self._port = port
                    self.log.info("Connected to %s @ %d baud", port, self._baudrate)
                    if self._on_connect:
                        self._on_connect(self)
                    return
                except BaseException as e:  # includes SerialException, OSError, etc.
                    last_exc = e
                    self._ser = None
                    self.log.warning("Connect failed (%s)", e)
                    # Decide whether to retry.
                    if self._max_retries >= 0 and attempt >= max(1, self._max_retries):
                        break
                    time.sleep(delay)
                    delay = min(
                        self._max_retry_delay,
                        delay * self._backoff_factor if delay else self._retry_delay,
                    )

            raise SerialException(
                f"Failed to open {port!r} after {attempt} attempt(s): {last_exc}"
            )

    def close(self) -> None:
        with self._lock:
            self._closing = True
            try:
                if self._ser and self._ser.is_open:
                    self._ser.close()
                    self.log.info("Closed serial port")
                    if self._on_disconnect:
                        self._on_disconnect(self)
            finally:
                self._ser = None
                self._closing = False

    def write(self, data: LineLike) -> int:
        """Write raw bytes or a string (encoded as utf-8). Returns bytes written.
        Auto-reconnects if enabled and the write fails.
        """
        if isinstance(data, str):
            payload = data.encode("utf-8")
        else:
            payload = bytes(data)

        def _try() -> int:
            if not self.is_open:
                self._maybe_reconnect()
            assert self._ser is not None
            return self._ser.write(payload)

        with self._lock:
            try:
                return _try()
            except BaseException as e:
                self.log.warning("Write error: %s", e)
                if not self._auto_reconnect:
                    raise
                self._force_reconnect()
                return _try()

    def write_line(self, line: LineLike, newline: bytes | str = b"\n") -> int:
        if isinstance(newline, str):
            newline_b = newline.encode("utf-8")
        else:
            newline_b = bytes(newline)
        if isinstance(line, str):
            payload = line.encode("utf-8") + newline_b
        else:
            payload = bytes(line) + newline_b
        return self.write(payload)

    def read(self, size: int = 1, *, timeout: Optional[float] = None) -> bytes:
        """Read up to *size* bytes. If *timeout* is given, temporarily overrides the
        default timeout for this call. Returns possibly fewer bytes if timeout occurs.
        Auto-reconnects if enabled and read fails.
        """
        with self._lock:
            if not self.is_open:
                self._maybe_reconnect()
            assert self._ser is not None
            original = self._ser.timeout
            try:
                if timeout is not None:
                    self._ser.timeout = timeout
                return self._read_with_reconnect(size)
            finally:
                if timeout is not None and self._ser:
                    self._ser.timeout = original

    def _read_with_reconnect(self, size: int) -> bytes:
        assert self._ser is not None
        try:
            return self._ser.read(size)
        except BaseException as e:
            self.log.warning("Read error: %s", e)
            if not self._auto_reconnect:
                raise
            self._force_reconnect()
            assert self._ser is not None
            return self._ser.read(size)

    def read_until(
        self,
        terminator: BytesLike = b"\n",
        *,
        timeout: Optional[float] = None,
        max_bytes: Optional[int] = None,
    ) -> bytes:
        """Read until *terminator* (included) or until *timeout*.
        Returns whatever has been read (may be empty) if timeout elapses.
        If *max_bytes* is set, stops when that many bytes have been accumulated.
        """
        if isinstance(terminator, str):
            term = terminator.encode("utf-8")
        else:
            term = bytes(terminator)

        end_time = (time.monotonic() + timeout) if timeout is not None else None
        buf = bytearray()
        while True:
            if end_time is not None and time.monotonic() >= end_time:
                break
            # Use a small chunk to be responsive to timeouts and reconnects
            chunk_timeout = max(
                0.05, min(0.5, (end_time - time.monotonic()) if end_time else 0.5)
            )
            chunk = self.read(1, timeout=chunk_timeout)
            if chunk:
                buf.extend(chunk)
                if buf.endswith(term):
                    break
                if max_bytes and len(buf) >= max_bytes:
                    break
        return bytes(buf)

    def readline(
        self, *, timeout: Optional[float] = None, max_bytes: Optional[int] = None
    ) -> bytes:
        return self.read_until(b"\n", timeout=timeout, max_bytes=max_bytes)

    def _maybe_reconnect(self) -> None:
        if self._auto_reconnect and not self.is_open and not self._closing:
            self._force_reconnect()
        elif not self.is_open:
            raise SerialException("Port is not open and auto_reconnect is disabled.")

    def _force_reconnect(self) -> None:
        # Save port in case it was auto-discovered previously.
        port = self._port or self.find_first_usb_serial()
        if not port:
            raise SerialException("Cannot reconnect: no serial port available.")

        self.log.info("Reconnecting to %s...", port)
        # Close any existing handle quietly
        try:
            if self._ser and self._ser.is_open:
                self._ser.close()
        except Exception:
            pass
        self._ser = None

        attempt = 0
        delay = max(0.0, self._retry_delay)
        last_exc: Optional[BaseException] = None
        while not self._closing:
            if self._stop_event.is_set():
                raise SerialException("Connect cancelled")

            attempt += 1
            try:
                ser = serial.Serial(port=port, **self._serial_kwargs)
                ser.setDTR(True)
                self._ser = ser
                self._port = port
                self.log.info("Reconnected to %s", port)
                if self._on_reconnect:
                    self._on_reconnect(self)
                return
            except BaseException as e:
                last_exc = e
                if self._max_retries >= 0 and attempt >= max(1, self._max_retries):
                    break
                time.sleep(delay)
                delay = min(
                    self._max_retry_delay,
                    delay * self._backoff_factor if delay else self._retry_delay,
                )
        raise SerialException(
            f"Reconnect to {port!r} failed after {attempt} attempt(s): {last_exc}"
        )

    def cancel_reconnects(self) -> None:
        """Tell reconnect/initial connect loops to stop ASAP."""
        self._stop_event.set()
        self._auto_reconnect = False

    @staticmethod
    def list_macos_ports() -> list[str]:
        """Return a list of likely macOS USB serial device paths.
        Includes `/dev/tty.usb*` and `/dev/tty.wchusb*` variants.
        """
        candidates: list[str] = []
        for p in list_ports.comports():
            if p.device.startswith("/dev/tty.usb") or p.device.startswith(
                "/dev/tty.wchusb"
            ):
                candidates.append(p.device)
        if not candidates:
            for p in list_ports.comports():
                if p.device.startswith("/dev/tty."):
                    candidates.append(p.device)
        return candidates

    @classmethod
    def find_first_usb_serial(cls) -> Optional[str]:
        ports = cls.list_macos_ports()
        return ports[0] if ports else None


if __name__ == "__main__":
    import argparse
    import time

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--port",
        type=str,
        default=None,
        help="Serial port path (default: auto-discover on macOS)",
    )
    ap.add_argument("--baud", type=int, default=115200, help="Baud rate")
    ap.add_argument(
        "--echo", type=str, default="Hello", help="Line to send for echo test"
    )
    ap.add_argument("--lines", type=int, default=1, help="Number of lines to send")
    ap.add_argument(
        "--timeout", type=float, default=1.0, help="Read timeout in seconds"
    )
    args = ap.parse_args()

    client = SerialClient(
        port=args.port,
        baudrate=args.baud,
        timeout=args.timeout,
        write_timeout=1.0,
        max_retries=-1,
        retry_delay=0.3,
        backoff_factor=1.8,
        max_retry_delay=3.0,
        auto_reconnect=True,
    )

    try:
        client.connect()
        while True:
            msg = f"{args.echo}"
            print(f"→ {msg}")
            client.write_line(msg)
            resp = client.readline(timeout=args.timeout)
            print(f"← {resp!r}")
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        client.close()

__all__ = [
    "SerialClient",
    "SerialException",
]
