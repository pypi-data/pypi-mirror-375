# config.py - 核心配置文件
import os
import sys
from pathlib import Path

from dynaconf import Dynaconf, Validator
from loguru import logger

from sytool import get_root_path

# 获取配置文件路径
ROOT_DIR = get_root_path()

config_path = ROOT_DIR / "config" / "config.yml"

if not config_path.exists():
    logger.error("配置文件不存在:{}", config_path)
    logger.info("如需执行程序，请在执行目录添加配置文件:config/config.yml")

# 基础配置对象 https://www.dynaconf.com/configuration/
settings = Dynaconf(
    # 配置参数[2,5](@ref)
    settings_files=[
        config_path,  # 主配置文件
        # 'D:\workspace\myself\gui_demo\config\.secrets.json',  # 加密配置文件
        # '.env',  # 环境变量文件
    ],
    environments=False,  # 启用多环境支持[3,6](@ref)
    # default_env="default",
    # env="development",  # 默认环境[3,6](@ref)
    env_switcher="MYAPP_ENV",  # 自定义环境变量名
    load_dotenv=False,  # 自动加载 .env 文件中的环境变量,默认 False，设为 True 启用
    dotenv_override=False,  # 覆盖已存在的环境变量[14](@ref)
    envvar_prefix="MYAPP",  # 环境变量前缀（如MYAPP_DATABASE__HOST）
    # dotenv_path=Path.cwd() / '.env',  # 指定.env文件路径[14](@ref)
    reload=True,  # 热更新开关[6,13](@ref)
    core_loaders=['YAML', 'TOML', 'JSON'],  # 支持的格式[5](@ref)
    secrets=["DATABASE.PASSWORD", "API_SECRET"],  # 加密字段标识
)


# 动态环境切换方法[3](@ref)
def switch_env(env: str):
    """切换运行环境"""
    os.environ["MYAPP_ENV"] = env
    # 重载配置
    settings.reload()


# 敏感信息解密示例[10](@ref)
def get_decrypted_password():
    return settings.get('DATABASE.PASSWORD')


settings.validators.register(
        Validator("monitor_dir", must_exist=True, is_type_of=str, is_dir=True),
        Validator("database", must_exist=True, is_type_of=dict),
        Validator("database.type", must_exist=True, is_type_of=str, choices=["mysql", "sqlserver","oracle"]),
        Validator("mapping_rules", must_exist=True, is_type_of=list)
    )


if __name__ == '__main__':
    print("当前环境配置:", settings.current_env)
    # 注册验证规则
    settings.validators.register(
        Validator("DATABASE.PORT", must_exist=True, is_type_of=int, gte=1024),
        Validator("API_ENDPOINT", is_type_of=str, condition=lambda v: v.startswith("http")),
        Validator("FEATURE_FLAGS.NEW_UI", default=False)  # 设置默认值[5,13](@ref)
    )

    # 执行验证（失败抛出 ValidationError）
    settings.validators.validate()

    # 安全读取（带默认值和类型转换）
    # retries = settings.get("RETRIES", default=3, cast=int)  # 强制转为整数
    print('retries:', settings.get('RETRIES', default=3))

    # 读取配置（支持点语法和字典访问）
    print(f"Database Host: {settings.database.host}")  # 默认环境为 development
    print(f"API Key: {settings.get('api_key')}")  # 输出环境变量覆盖后的值

    # 动态切换环境（如切换到生产环境）
    # settings.setenv("production")
    # print(f"Production DB Password: {settings.database.password}")  # 从 .secrets.yaml 读取

    # 临时更新配置（仅内存生效）
    settings.set("CACHE_TIMEOUT", 3600)

    # 批量更新配置
    settings.update({"LOG_LEVEL": "DEBUG", "THREAD_POOL": 8}, force_save=True)

    print('database.password', get_decrypted_password())

    # settings.reload()

    # 持久化配置到文件（保存为 TOML 格式）

    # write(settings.as_dict(), "settings.toml")  # 将当前配置写入文件

    #
    #
    # # 方式2：通过装饰器监听特定配置变化
    # @settings.onloaded
    # def on_settings_loaded(settings):
    #     print("配置已更新：", settings.as_dict())

    from dynaconf.utils import encode, decode

    # 加密配置值
    secret = encode('my_password', key='加密密钥')
    print('my_password:', settings.get('password'))
    settings.set('password', secret)
    print('my_password:', settings.get('password'))

    # 解密使用
    password = decode(settings.password, key='加密密钥')
    print('my_password:', password)

    # while True:
    #     time.sleep(10)
    #     print('database.username', get_decrypted_password())
