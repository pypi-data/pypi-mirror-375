import socket
import threading
import json
import time

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.messages = []
        self.lock = threading.Lock()
        self.is_running = True
        self._recv_buffer = ""
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()
    
    def receive_messages(self):
        while self.is_running:
            try:
                chunk = self.client_socket.recv(4096).decode('utf-8')
                if not chunk:
                    break
                self._recv_buffer += chunk
                self.lock.acquire()
                while "\n" in self._recv_buffer:
                    line, self._recv_buffer = self._recv_buffer.split("\n", 1)
                    if line:
                        self.messages.append(line)
                self.lock.release()
            except:
                break
    
    def send_message(self, message):
        self.client_socket.send((str(message) + "\n").encode('utf-8'))
    
    def get_messages(self):
        self.lock.acquire()
        messages = self.messages
        self.messages = []
        self.lock.release()
        return messages
    
    def listenconfirm(self, timeout=None):
        start_time = time.time()
        while True:
            self.lock.acquire()
            confirm_code = None
            for i, message in enumerate(self.messages):
                if isinstance(message, str) and message.startswith("__CONFIRM__:"):
                    confirm_code = message.split(":", 1)[1]
                    del self.messages[i]
                    break
            self.lock.release()
            if confirm_code is not None:
                return confirm_code
            if timeout is not None and (time.time() - start_time) >= timeout:
                return None
            time.sleep(0.05)
    
    def close(self):
        self.is_running = False
        self.client_socket.close()
        self.receive_thread.join()

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        # Short timeout so accept() can periodically check is_running and exit cleanly
        try:
            self.server_socket.settimeout(0.2)
        except Exception:
            pass
        self.clients = []
        self.messages = []
        self.lock = threading.Lock()
        self.is_running = True
        self.on_connect_callback = None
        self.on_disconnect_callback = None
        self.on_idle_callback = None
        self.idle_timeout_seconds = None
        self._client_last_activity = {}
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()
    
    def receive_messages(self):
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
            except (socket.timeout, TimeoutError):
                continue
            except OSError:
                if not self.is_running:
                    break
                else:
                    continue
            except Exception:
                if not self.is_running:
                    break
                else:
                    continue
            self.lock.acquire()
            self.clients.append(client_socket)
            self.lock.release()
            # Initialize last activity for this client
            try:
                self._client_last_activity[client_socket] = time.time()
            except Exception:
                pass
            # Invoke on-connect hooks
            if self.on_connect_callback is not None:
                try:
                    self.on_connect_callback(client_socket, client_address)
                except Exception:
                    pass
            # Backwards-compatible hook; no-op unless overridden
            try:
                self.onconnect(client_socket, client_address)
            except Exception:
                pass
            try:
                client_socket.settimeout(1.0)
            except Exception:
                pass
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()
    
    def handle_client(self, client_socket, client_address):
        last_activity_time = time.time()
        while self.is_running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                last_activity_time = time.time()
                try:
                    self._client_last_activity[client_socket] = last_activity_time
                except Exception:
                    pass
                message = data.decode('utf-8')
                self.lock.acquire()
                self.messages.append(message)
                self.lock.release()
            except socket.timeout:
                # Check idle via OnIdle helper; it runs action and disconnects if needed
                try:
                    if self.OnIdle(client_socket, client_address):
                        break
                except Exception:
                    pass
                continue
            except Exception:
                break
        # Cleanup on disconnect
        self.lock.acquire()
        try:
            if client_socket in self.clients:
                try:
                    self.clients.remove(client_socket)
                except Exception:
                    pass
        finally:
            self.lock.release()
        try:
            client_socket.close()
        except Exception:
            pass
        if self.on_disconnect_callback is not None:
            try:
                self.on_disconnect_callback(client_socket, client_address)
            except Exception:
                pass
    
    def set_idle_timeout(self, seconds):
        self.idle_timeout_seconds = seconds

    def OnIdle(self, client_socket, client_address, action=None):
        """Verifica inatividade e desconecta o cliente se exceder o limite.

        Retorna True se o cliente foi desconectado por inatividade, caso contrário False.
        """
        if self.idle_timeout_seconds is None:
            return False
        try:
            last_activity_time = self._client_last_activity.get(client_socket)
        except Exception:
            last_activity_time = None
        if last_activity_time is None:
            # Se não soubermos, assume ativo agora
            try:
                self._client_last_activity[client_socket] = time.time()
            except Exception:
                pass
            return False
        if (time.time() - last_activity_time) > self.idle_timeout_seconds:
            # Executa ação customizada, se fornecida (ou registrada)
            try:
                callback = action if action is not None else self.on_idle_callback
                if callable(callback):
                    callback(client_socket, client_address)
            except Exception:
                pass
            # Desconectar este cliente
            self.lock.acquire()
            try:
                if client_socket in self.clients:
                    try:
                        self.clients.remove(client_socket)
                    except Exception:
                        pass
            finally:
                self.lock.release()
            try:
                client_socket.close()
            except Exception:
                pass
            if self.on_disconnect_callback is not None:
                try:
                    self.on_disconnect_callback(client_socket, client_address)
                except Exception:
                    pass
            return True
        return False

    def on_idle(self, callback):
        """Registra uma ação a ser executada quando um cliente ficar inativo.

        A função recebe (client_socket, client_address).
        """
        self.on_idle_callback = callback
    
    def send_message(self, message):
        self.lock.acquire()
        try:
            for client in self.clients:
                try:
                    client.send((str(message) + "\n").encode('utf-8'))
                except Exception:
                    pass
        finally:
            self.lock.release()
    
    def get_messages(self):
        self.lock.acquire()
        messages = self.messages
        self.messages = []
        self.lock.release()
        return messages
    
    def close(self):
        self.is_running = False
        try:
            self.server_socket.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            self.server_socket.close()
        except Exception:
            pass
        self.receive_thread.join()
    def broadcast_message(self, message):
        self.lock.acquire()
        try:
            for client in self.clients:
                try:
                    client.send((str(message) + "\n").encode('utf-8'))
                except Exception:
                    pass
        finally:
            self.lock.release()
    def send_message(self, message, client_socket):
        client_socket.send((str(message) + "\n").encode('utf-8'))

    def get_clients(self):
        self.lock.acquire()
        clients = self.clients
        self.lock.release()
        return clients

    def get_client_by_address(self, address):
        for client in self.clients:
            if client.getpeername()[0] == address:
                return client
    def save_connected_clients(self):
        # Save addresses only; sockets are not JSON-serializable
        addresses = []
        for client in self.clients:
            try:
                addresses.append(client.getpeername())
            except Exception:
                pass
        with open("connected_clients.json", "w") as f:
            json.dump(addresses, f)
    def load_connected_clients(self):
        # Returns list of addresses previously saved
        try:
            with open("connected_clients.json", "r") as f:
                return json.load(f)
        except Exception:
            return []
    def get_connected_clients(self):
        return self.clients
    def get_connected_clients_count(self):
        return len(self.clients)
    def get_connected_clients_addresses(self):
        return [client.getpeername()[0] for client in self.clients]
   
    # Removed invalid name/status getters; getpeername returns (host, port)
    
    def on_connect(self, callback):
        """Register a function to be called when a client connects.

        The callback receives (client_socket, client_address).
        """
        self.on_connect_callback = callback
    def on_disconnect(self, callback):
        self.on_disconnect_callback = callback
    def accept_connection(self, client_socket, client_address):
        self.lock.acquire()
        self.clients.append(client_socket)
        self.lock.release()
        if self.on_connect_callback is not None:
            try:
                self.on_connect_callback(client_socket, client_address)
            except Exception:
                pass

    def reject_connection(self, client_socket, client_address):
        self.lock.acquire()
        try:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
        finally:
            self.lock.release()
        if self.on_disconnect_callback is not None:
            try:
                self.on_disconnect_callback(client_socket, client_address)
            except Exception:
                pass

    def kill_client_by_address(self, address):
        for client in self.clients:
            if client.getpeername()[0] == address:
                self.clients.remove(client)
                client.close()
                break



class LocalConnection:
    def __init__(self):
        self.clients = []
        self.lock = threading.Lock()
        self.is_running = True
        self.messages = []
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()
    def receive_messages(self):
        while self.is_running:
            if not self.clients:
                time.sleep(0.05)
                continue
            try:
                message = self.clients[0].recv(4096).decode('utf-8')
                self.lock.acquire()
                for line in message.split("\n"):
                    if line:
                        self.messages.append(line)
                self.lock.release()
            except Exception:
                time.sleep(0.05)
    def send_message(self, message):
        if self.clients:
            try:
                self.clients[0].send((str(message) + "\n").encode('utf-8'))
            except Exception:
                pass
        else:
            self.lock.acquire()
            self.messages.append(message)
            self.lock.release()
    def get_messages(self):
        self.lock.acquire()
        messages = self.messages
        self.messages = []
        self.lock.release()
        return messages
    def listenconfirm(self, timeout=None):
        start_time = time.time()
        while True:
            self.lock.acquire()
            confirm_code = None
            for i, message in enumerate(self.messages):
                if isinstance(message, str) and message.startswith("__CONFIRM__:"):
                    confirm_code = message.split(":", 1)[1]
                    del self.messages[i]
                    break
            self.lock.release()
            if confirm_code is not None:
                return confirm_code
            if timeout is not None and (time.time() - start_time) >= timeout:
                return None
            time.sleep(0.05)
    
    def confirm_message(self, code):
        if self.clients:
            try:
                self.clients[0].send((f"__CONFIRM__:{code}" + "\n").encode('utf-8'))
            except Exception:
                pass
        else:
            self.lock.acquire()
            self.messages.append(f"__CONFIRM__:{code}")
            self.lock.release()
   
    def close(self):
        self.is_running = False
        try:
            self.receive_thread.join()
        except Exception:
            pass

    def attach_client_socket(self, client_socket):
        """Attach an existing socket as the local endpoint."""
        self.lock.acquire()
        self.clients.append(client_socket)
        self.lock.release()
class Locker:
    def __init__(self):
        self._lock = threading.Lock()

    def lock(self):
        self._lock.acquire()

    def unlock(self):
        self._lock.release()

    def thread_lock(self):
        return threading.Lock()

    def thread_unlock(self, lock_obj):
        try:
            lock_obj.release()
        except Exception:
            pass

