
"""
統一配置管理模組
實現 Singleton 模式確保全域配置一致性
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field


@dataclass
class RedmineConfig:
    """Redmine 相關配置"""
    base_url: str = "https://redmine.etzone.net"
    request_delay: float = 1.0
    timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    max_retries: int = 3
    retry_delay: float = 2.0
    # 可選的 Redmine session cookie，優先以環境變數或設定檔覆蓋
    session_cookie: str = ""


@dataclass
class PathConfig:
    """路徑相關配置"""
    output_dir: str = "redmine_output"
    pdf_dir: str = "pdfs"
    attachments_dir: str = "attachments"
    log_dir: str = "logs"
    cache_dir: str = "cache"


@dataclass
class PdfConfig:
    """PDF 生成配置"""
    page_size: str = "A4"
    margin_top: str = "0.75in"
    margin_right: str = "0.75in"
    margin_bottom: str = "0.75in"
    margin_left: str = "0.75in"
    encoding: str = "UTF-8"
    javascript_delay: int = 1000
    enable_local_file_access: bool = True
    no_outline: bool = True
    wkhtmltopdf_path: str = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"


@dataclass
class SecurityConfig:
    """安全相關配置"""
    allowed_domains: list = field(default_factory=lambda: ["redmine.etzone.net"])
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_file_extensions: list = field(default_factory=lambda: [
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff",
        ".zip", ".rar", ".7z", ".tar", ".gz",
        ".txt", ".csv", ".xml", ".json"
    ])


@dataclass
class LogConfig:
    """日誌配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_name: str = "redmine_crawler.log"
    max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True


class ConfigManager:
    """
    配置管理器 - 實現 Singleton 模式
    統一管理所有配置參數，支援環境變數覆蓋和配置檔案載入
    """
    _instance: Optional['ConfigManager'] = None
    _initialized: bool = False

    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化配置管理器"""
        if self._initialized:
            return
        
        self._config_file_path: Optional[Path] = None
        self._redmine_config = RedmineConfig()
        self._path_config = PathConfig()
        self._pdf_config = PdfConfig()
        self._security_config = SecurityConfig()
        self._log_config = LogConfig()


        # 載入環境變數和配置檔案
        self._load_from_environment()
        self._load_from_file()

        self._initialized = True

    @property
    def redmine(self) -> RedmineConfig:
        """獲取 Redmine 配置"""
        return self._redmine_config

    @property
    def paths(self) -> PathConfig:
        """獲取路徑配置"""
        return self._path_config

    @property
    def pdf(self) -> PdfConfig:
        """獲取 PDF 配置"""
        return self._pdf_config

    @property
    def security(self) -> SecurityConfig:
        """獲取安全配置"""
        return self._security_config

    @property
    def log(self) -> LogConfig:
        """獲取日誌配置"""
        return self._log_config

    def load_config_file(self, file_path: Union[str, Path]) -> None:
        """
        載入配置檔案
        
        Args:
            file_path: 配置檔案路徑
        """
        self._config_file_path = Path(file_path)
        self._load_from_file()

    def save_config_file(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """
        儲存配置到檔案
        
        Args:
            file_path: 配置檔案路徑，若未指定則使用預設路徑
        """
        if file_path is None:
            file_path = self._config_file_path or Path("config.json")
        else:
            file_path = Path(file_path)
        
        config_data = {
            "redmine": self._dataclass_to_dict(self._redmine_config),
            "paths": self._dataclass_to_dict(self._path_config),
            "pdf": self._dataclass_to_dict(self._pdf_config),
            "security": self._dataclass_to_dict(self._security_config),
            "log": self._dataclass_to_dict(self._log_config)
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def update_config(self, section: str, **kwargs) -> None:
        """
        更新配置
        
        Args:
            section: 配置區段名稱 (redmine, paths, pdf, security, log)
            **kwargs: 要更新的配置參數
        """
        config_map = {
            "redmine": self._redmine_config,
            "paths": self._path_config,
            "pdf": self._pdf_config,
            "security": self._security_config,
            "log": self._log_config
        }
        
        if section not in config_map:
            raise ValueError(f"未知的配置區段: {section}")
        
        config_obj = config_map[section]
        for key, value in kwargs.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
            else:
                raise ValueError(f"配置區段 {section} 中沒有 {key} 參數")

    def get_pdf_options(self) -> Dict[str, Any]:
        """
        獲取 PDF 生成選項
        
        Returns:
            PDF 生成選項字典
        """
        return {
            'page-size': self._pdf_config.page_size,
            'margin-top': self._pdf_config.margin_top,
            'margin-right': self._pdf_config.margin_right,
            'margin-bottom': self._pdf_config.margin_bottom,
            'margin-left': self._pdf_config.margin_left,
            'encoding': self._pdf_config.encoding,
            'javascript-delay': self._pdf_config.javascript_delay,
            'enable-local-file-access': None if self._pdf_config.enable_local_file_access else False,
            'no-outline': None if self._pdf_config.no_outline else False
        }

    def get_absolute_path(self, relative_path: str) -> Path:
        """
        獲取絕對路徑
        
        Args:
            relative_path: 相對路徑
            
        Returns:
            絕對路徑
        """
        base_path = Path(self._path_config.output_dir)
        return base_path / relative_path

    def validate_configuration(self) -> list:
        """
        驗證配置有效性
        
        Returns:
            錯誤列表，空列表表示無錯誤
        """
        errors = []
        
        # 驗證 wkhtmltopdf 路徑
        if not Path(self._pdf_config.wkhtmltopdf_path).exists():
            errors.append(f"wkhtmltopdf 路徑不存在: {self._pdf_config.wkhtmltopdf_path}")
        
        # 驗證 URL 格式
        if not self._redmine_config.base_url.startswith(('http://', 'https://')):
            errors.append(f"無效的 base_url 格式: {self._redmine_config.base_url}")
        
        # 驗證數值範圍
        if self._redmine_config.request_delay < 0:
            errors.append(f"request_delay 不能為負數: {self._redmine_config.request_delay}")
        
        if self._redmine_config.timeout <= 0:
            errors.append(f"timeout 必須為正數: {self._redmine_config.timeout}")
        
        return errors

    def _load_from_environment(self) -> None:
        """從環境變數載入配置"""
        # Redmine 配置
        if base_url := os.getenv('REDMINE_BASE_URL'):
            self._redmine_config.base_url = base_url
        
        if request_delay := os.getenv('REDMINE_REQUEST_DELAY'):
            try:
                self._redmine_config.request_delay = float(request_delay)
            except ValueError:
                pass
        
        if timeout := os.getenv('REDMINE_TIMEOUT'):
            try:
                self._redmine_config.timeout = int(timeout)
            except ValueError:
                pass

        # Session cookie (可選)
        if session_cookie := os.getenv('REDMINE_SESSION_COOKIE'):
            self._redmine_config.session_cookie = session_cookie
        
        # 路徑配置
        if output_dir := os.getenv('REDMINE_OUTPUT_DIR'):
            self._path_config.output_dir = output_dir
        
        # PDF 配置
        if wkhtmltopdf_path := os.getenv('WKHTMLTOPDF_PATH'):
            self._pdf_config.wkhtmltopdf_path = wkhtmltopdf_path

    def _load_dotenv(self) -> None:
        """簡單的 .env 載入器：讀取專案根目錄的 .env，將變數加入 os.environ（若尚未存在才加入）。

        支援格式：KEY=VALUE，會忽略以 # 開頭的註解與空行。
        """
        try:
            # 嘗試在專案根目錄（工作目錄）尋找 .env
            dotenv_path = Path('.') / '.env'
            if not dotenv_path.exists():
                return

            with dotenv_path.open('r', encoding='utf-8') as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    # 只有在該環境變數尚未被設定時才加入
                    if key and key not in os.environ:
                        os.environ[key] = val
        except Exception:
            # 不要因為 .env 的讀取失敗而阻斷程序，僅印出簡短警告
            print('警告: 載入 .env 時發生錯誤，已跳過 .env 讀取。')

    def _load_from_file(self) -> None:
        """從檔案載入配置"""
        if self._config_file_path is None or not self._config_file_path.exists():
            return
        
        try:
            with open(self._config_file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 更新各配置區段
            if 'redmine' in config_data:
                self._update_dataclass_from_dict(self._redmine_config, config_data['redmine'])
            
            if 'paths' in config_data:
                self._update_dataclass_from_dict(self._path_config, config_data['paths'])
            
            if 'pdf' in config_data:
                self._update_dataclass_from_dict(self._pdf_config, config_data['pdf'])
            
            if 'security' in config_data:
                self._update_dataclass_from_dict(self._security_config, config_data['security'])
            
            if 'log' in config_data:
                self._update_dataclass_from_dict(self._log_config, config_data['log'])
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"警告: 載入配置檔案失敗: {e}")

    @staticmethod
    def _dataclass_to_dict(obj) -> Dict[str, Any]:
        """將 dataclass 轉換為字典"""
        return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}

    @staticmethod
    def _update_dataclass_from_dict(obj, data: Dict[str, Any]) -> None:
        """從字典更新 dataclass"""
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)


# 全域配置實例
config = ConfigManager()
