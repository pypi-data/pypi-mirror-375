"""
CausalLLM Configuration Management System

This module provides centralized configuration management with environment variable support,
validation, and type safety for all CausalLLM components.
"""

import os
import json
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM providers and models."""
    provider: Optional[str] = None  # 'openai', 'anthropic', 'llama', 'mcp'
    model: Optional[str] = None
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    temperature: float = 0.0


@dataclass
class PerformanceConfig:
    """Configuration for performance optimizations."""
    enable_optimizations: bool = True
    use_async: bool = False
    chunk_size: Union[int, str] = 'auto'
    max_memory_gb: Optional[float] = None
    cache_enabled: bool = True
    cache_dir: Optional[str] = None
    cache_size_gb: float = 1.0
    parallel_processing: bool = True
    max_workers: Optional[int] = None


@dataclass
class StatisticalConfig:
    """Configuration for statistical methods and inference."""
    significance_level: float = 0.05
    confidence_level: float = 0.95
    bootstrap_samples: int = 1000
    max_conditioning_set_size: int = 2
    min_sample_size: int = 50
    robust_methods: bool = True
    assumption_testing: bool = True


@dataclass
class LoggingConfig:
    """Configuration for logging and debugging."""
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_path: Optional[str] = None
    max_file_size: str = '10MB'
    backup_count: int = 5
    enable_progress_bars: bool = True


@dataclass
class SecurityConfig:
    """Configuration for security and privacy settings."""
    mask_sensitive_data: bool = True
    log_api_calls: bool = False
    encrypt_cache: bool = False
    data_retention_days: Optional[int] = None


@dataclass
class CausalLLMConfig:
    """Main configuration class for CausalLLM."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    statistical: StatisticalConfig = field(default_factory=StatisticalConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Global settings
    environment: str = 'production'  # 'development', 'testing', 'production'
    debug: bool = False
    profile: bool = False
    
    def __post_init__(self):
        """Validate and process configuration after initialization."""
        self._validate_config()
        self._apply_environment_overrides()
    
    def _validate_config(self):
        """Validate configuration values."""
        # Validate significance level
        if not 0 < self.statistical.significance_level < 1:
            raise ValueError("significance_level must be between 0 and 1")
        
        # Validate confidence level
        if not 0 < self.statistical.confidence_level < 1:
            raise ValueError("confidence_level must be between 0 and 1")
        
        # Validate memory settings
        if isinstance(self.performance.max_memory_gb, (int, float)) and self.performance.max_memory_gb <= 0:
            raise ValueError("max_memory_gb must be positive")
        
        # Validate cache settings
        if self.performance.cache_size_gb <= 0:
            raise ValueError("cache_size_gb must be positive")
        
        # Validate logging level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level.upper() not in valid_levels:
            raise ValueError(f"logging.level must be one of {valid_levels}")
    
    def _apply_environment_overrides(self):
        """Apply environment variable overrides."""
        # LLM Configuration
        if os.getenv('CAUSALLM_LLM_PROVIDER'):
            self.llm.provider = os.getenv('CAUSALLM_LLM_PROVIDER')
        if os.getenv('CAUSALLM_LLM_MODEL'):
            self.llm.model = os.getenv('CAUSALLM_LLM_MODEL')
        if os.getenv('OPENAI_API_KEY'):
            self.llm.api_key = os.getenv('OPENAI_API_KEY')
        if os.getenv('ANTHROPIC_API_KEY') and self.llm.provider == 'anthropic':
            self.llm.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Performance Configuration
        if os.getenv('CAUSALLM_ENABLE_OPTIMIZATIONS'):
            self.performance.enable_optimizations = os.getenv('CAUSALLM_ENABLE_OPTIMIZATIONS').lower() == 'true'
        if os.getenv('CAUSALLM_USE_ASYNC'):
            self.performance.use_async = os.getenv('CAUSALLM_USE_ASYNC').lower() == 'true'
        if os.getenv('CAUSALLM_CHUNK_SIZE'):
            chunk_size = os.getenv('CAUSALLM_CHUNK_SIZE')
            self.performance.chunk_size = chunk_size if chunk_size == 'auto' else int(chunk_size)
        if os.getenv('CAUSALLM_MAX_MEMORY_GB'):
            self.performance.max_memory_gb = float(os.getenv('CAUSALLM_MAX_MEMORY_GB'))
        if os.getenv('CAUSALLM_CACHE_DIR'):
            self.performance.cache_dir = os.getenv('CAUSALLM_CACHE_DIR')
        
        # Statistical Configuration
        if os.getenv('CAUSALLM_SIGNIFICANCE_LEVEL'):
            self.statistical.significance_level = float(os.getenv('CAUSALLM_SIGNIFICANCE_LEVEL'))
        if os.getenv('CAUSALLM_CONFIDENCE_LEVEL'):
            self.statistical.confidence_level = float(os.getenv('CAUSALLM_CONFIDENCE_LEVEL'))
        
        # Logging Configuration
        if os.getenv('CAUSALLM_LOG_LEVEL'):
            self.logging.level = os.getenv('CAUSALLM_LOG_LEVEL').upper()
        if os.getenv('CAUSALLM_LOG_FILE'):
            self.logging.file_path = os.getenv('CAUSALLM_LOG_FILE')
        
        # Global settings
        if os.getenv('CAUSALLM_ENVIRONMENT'):
            self.environment = os.getenv('CAUSALLM_ENVIRONMENT')
        if os.getenv('CAUSALLM_DEBUG'):
            self.debug = os.getenv('CAUSALLM_DEBUG').lower() == 'true'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self)
    
    def save(self, file_path: Union[str, Path]):
        """Save configuration to JSON file."""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        logger.info(f"Configuration saved to {file_path}")
    
    @classmethod
    def load(cls, file_path: Union[str, Path]) -> 'CausalLLMConfig':
        """Load configuration from JSON file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Reconstruct nested dataclass objects
        config = cls()
        if 'llm' in data:
            config.llm = LLMConfig(**data['llm'])
        if 'performance' in data:
            config.performance = PerformanceConfig(**data['performance'])
        if 'statistical' in data:
            config.statistical = StatisticalConfig(**data['statistical'])
        if 'logging' in data:
            config.logging = LoggingConfig(**data['logging'])
        if 'security' in data:
            config.security = SecurityConfig(**data['security'])
        
        # Set global settings
        for key in ['environment', 'debug', 'profile']:
            if key in data:
                setattr(config, key, data[key])
        
        logger.info(f"Configuration loaded from {file_path}")
        return config
    
    def copy(self) -> 'CausalLLMConfig':
        """Create a deep copy of the configuration."""
        return CausalLLMConfig(
            llm=LLMConfig(**asdict(self.llm)),
            performance=PerformanceConfig(**asdict(self.performance)),
            statistical=StatisticalConfig(**asdict(self.statistical)),
            logging=LoggingConfig(**asdict(self.logging)),
            security=SecurityConfig(**asdict(self.security)),
            environment=self.environment,
            debug=self.debug,
            profile=self.profile
        )
    
    def update(self, **kwargs):
        """Update configuration with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if isinstance(value, dict) and hasattr(getattr(self, key), '__dict__'):
                    # Update nested configuration
                    nested_config = getattr(self, key)
                    for nested_key, nested_value in value.items():
                        if hasattr(nested_config, nested_key):
                            setattr(nested_config, nested_key, nested_value)
                else:
                    setattr(self, key, value)
        
        self._validate_config()


class ConfigManager:
    """Singleton configuration manager for CausalLLM."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = CausalLLMConfig()
    
    @property
    def config(self) -> CausalLLMConfig:
        """Get the current configuration."""
        return self._config
    
    def load_config(self, file_path: Optional[Union[str, Path]] = None) -> CausalLLMConfig:
        """Load configuration from file or create default."""
        if file_path and Path(file_path).exists():
            self._config = CausalLLMConfig.load(file_path)
        else:
            # Look for default config files
            default_paths = [
                Path.cwd() / 'causallm.json',
                Path.home() / '.causallm' / 'config.json',
                Path.cwd() / 'config' / 'causallm.json'
            ]
            
            for default_path in default_paths:
                if default_path.exists():
                    self._config = CausalLLMConfig.load(default_path)
                    logger.info(f"Loaded configuration from {default_path}")
                    break
            else:
                # Use default configuration
                self._config = CausalLLMConfig()
                logger.info("Using default configuration")
        
        return self._config
    
    def save_config(self, file_path: Optional[Union[str, Path]] = None):
        """Save current configuration to file."""
        if file_path is None:
            file_path = Path.cwd() / 'causallm.json'
        
        self._config.save(file_path)
    
    def update_config(self, **kwargs):
        """Update current configuration."""
        self._config.update(**kwargs)
    
    def reset_config(self):
        """Reset to default configuration."""
        self._config = CausalLLMConfig()
    
    def get_environment_config(self) -> Dict[str, str]:
        """Get environment variables for current configuration."""
        env_vars = {}
        
        # LLM settings
        if self._config.llm.provider:
            env_vars['CAUSALLM_LLM_PROVIDER'] = self._config.llm.provider
        if self._config.llm.model:
            env_vars['CAUSALLM_LLM_MODEL'] = self._config.llm.model
        
        # Performance settings
        env_vars['CAUSALLM_ENABLE_OPTIMIZATIONS'] = str(self._config.performance.enable_optimizations).lower()
        env_vars['CAUSALLM_USE_ASYNC'] = str(self._config.performance.use_async).lower()
        env_vars['CAUSALLM_CHUNK_SIZE'] = str(self._config.performance.chunk_size)
        
        if self._config.performance.max_memory_gb:
            env_vars['CAUSALLM_MAX_MEMORY_GB'] = str(self._config.performance.max_memory_gb)
        
        if self._config.performance.cache_dir:
            env_vars['CAUSALLM_CACHE_DIR'] = self._config.performance.cache_dir
        
        # Statistical settings
        env_vars['CAUSALLM_SIGNIFICANCE_LEVEL'] = str(self._config.statistical.significance_level)
        env_vars['CAUSALLM_CONFIDENCE_LEVEL'] = str(self._config.statistical.confidence_level)
        
        # Logging settings
        env_vars['CAUSALLM_LOG_LEVEL'] = self._config.logging.level
        
        # Global settings
        env_vars['CAUSALLM_ENVIRONMENT'] = self._config.environment
        env_vars['CAUSALLM_DEBUG'] = str(self._config.debug).lower()
        
        return env_vars


# Global configuration instance
config_manager = ConfigManager()

# Convenience functions
def get_config() -> CausalLLMConfig:
    """Get the global configuration instance."""
    return config_manager.config

def load_config(file_path: Optional[Union[str, Path]] = None) -> CausalLLMConfig:
    """Load configuration from file."""
    return config_manager.load_config(file_path)

def save_config(file_path: Optional[Union[str, Path]] = None):
    """Save current configuration to file."""
    config_manager.save_config(file_path)

def update_config(**kwargs):
    """Update global configuration."""
    config_manager.update_config(**kwargs)

def reset_config():
    """Reset to default configuration."""
    config_manager.reset_config()