import socket
import json
from datetime import datetime, timedelta


class ElegooSaturn3Ultra:
    def __init__(self, ip: str, port: int = 3000, timeout: int = 20):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.buff_size = 4096
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(self.timeout)

    def _send_command(self, command: str) -> dict:
        """Envia um comando para a impressora e retorna a resposta em JSON."""
        try:
            self.sock.sendto(command.encode(), (self.ip, self.port))
            response, _ = self.sock.recvfrom(self.buff_size)
            # Converte resposta JSON para dicionário Python
            return json.loads(response.decode())
        except socket.timeout:
            print("Timeout: Nenhuma resposta recebida da impressora.")
            return {}
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON da resposta.")
            return {}

    def get_printer_name(self) -> str:
        """Retorna o nome da impressora."""
        response = self._send_command("M99999")
        return response.get("Data", {}).get("Attributes", {}).get("MachineName", "Desconhecido")

    def get_firmware_version(self) -> str:
        """Retorna a versão do firmware da impressora."""
        response = self._send_command("M99999")
        return response.get("Data", {}).get("Attributes", {}).get("FirmwareVersion", "Desconhecido")

    def get_resolution(self) -> str:
        """Retorna a resolução de impressão da impressora."""
        response = self._send_command("M99999")
        return response.get("Data", {}).get("Attributes", {}).get("Resolution", "Desconhecido")

    def get_status(self) -> str:
        """Retorna o status atual da impressora."""
        response = self._send_command("M99999")
        status_code = response.get("Data", {}).get("Status", {}).get("CurrentStatus", -1)
        # Traduz o código de status para uma mensagem legível
        status_map = {0: "Idle", 1: "Printing", 2: "Paused", 3: "Error"}
        return status_map.get(status_code, "Status desconhecido")

    def get_print_progress(self) -> dict:
        """Retorna o progresso da impressão atual, incluindo tempo decorrido, tempo restante e porcentagem."""
        response = self._send_command("M99999")
        print_info = response.get("Data", {}).get("Status", {}).get("PrintInfo", {})

        # Extraindo informações relevantes
        current_layer = print_info.get("CurrentLayer", 0)
        total_layers = print_info.get("TotalLayer", 0)
        elapsed_ticks = print_info.get("CurrentTicks", 0)
        total_ticks = print_info.get("TotalTicks", 0)
        filename = print_info.get("Filename", "")

        # Calcular porcentagens e tempos
        percentage = (current_layer / total_layers * 100) if total_layers > 0 else 0
        elapsed_time = self._ticks_to_time(elapsed_ticks)
        remaining_time = self._ticks_to_time(total_ticks - elapsed_ticks) if total_ticks > elapsed_ticks else "0s"

        estimated_finish_time = self._calculate_estimated_finish_time(elapsed_ticks, total_ticks)

        return {
            "CurrentLayer": current_layer,
            "TotalLayer": total_layers,
            "Filename": filename,
            "ElapsedTime": elapsed_time,
            "RemainingTime": remaining_time,
            "Percentage": f"{percentage:.2f}%",  # Formatação com duas casas decimais
            "EstimatedFinishTime": estimated_finish_time
        }

    def _ticks_to_time(self, ticks: int) -> str:
        """Converte ticks em um formato legível de tempo (horas:minutos:segundos)."""
        seconds = ticks // 1000  # Supondo que os ticks estejam em milissegundos
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def _calculate_estimated_finish_time(self, elapsed_ticks: int, total_ticks: int) -> str:
        """Calcula a hora estimada de finalização da impressão no formato HH:MM:SS - DD/MM/AA."""
        if total_ticks <= elapsed_ticks:
            return "Impressão concluída"

        elapsed_time_seconds = elapsed_ticks / 1000  # Converte ticks para segundos
        remaining_ticks = total_ticks - elapsed_ticks
        remaining_time_seconds = remaining_ticks / 1000  # Converte ticks restantes para segundos

        # Hora atual
        now = datetime.now()
        # Calcula a hora de finalização estimada
        estimated_finish = now + timedelta(seconds=remaining_time_seconds)
        return estimated_finish.strftime("%H:%M:%S - %d/%m/%y")

    def get_printer_info(self) -> dict:
        """Retorna um JSON com as informações da impressora."""
        info = {
            "Nome da Impressora": self.get_printer_name(),
            "Versão do Firmware": self.get_firmware_version(),
            "Resolução": self.get_resolution(),
            "Status": self.get_status()
        }
        return info

    def get_status_info(self) -> dict:
        """Retorna um JSON com o status da impressora, incluindo progresso e tempo restante."""
        progress_info = self.get_print_progress()  # Utiliza o método que já retorna o progresso
        status_info = {
            "Status": self.get_status(),
            "Progresso da Impressão": {
                "Arquivo": progress_info["Filename"],
                "Camada Atual": progress_info["CurrentLayer"],
                "Total de Camadas": progress_info["TotalLayer"],
                "Tempo Decorrido": progress_info["ElapsedTime"],
                "Tempo Restante": progress_info["RemainingTime"],
                "Porcentagem": progress_info["Percentage"],
                "Tempo Estimado de Conclusão": progress_info["EstimatedFinishTime"]

            }
        }
        return status_info

# Exemplo de uso:
if __name__ == "__main__":
    printer = ElegooSaturn3Ultra("192.168.0.172")
    #print(f"Nome da Impressora: {printer.get_printer_name()}")
    #print(f"Versão do Firmware: {printer.get_firmware_version()}")
    #print(f"Resolução: {printer.get_resolution()}")
    #print(f"Status: {printer.get_status()}")
    #print(f"Progresso da Impressão: {printer.get_print_progress()}")

    printer_info = printer.get_status_info()
    print(json.dumps(printer_info, indent=4, ensure_ascii=False))
