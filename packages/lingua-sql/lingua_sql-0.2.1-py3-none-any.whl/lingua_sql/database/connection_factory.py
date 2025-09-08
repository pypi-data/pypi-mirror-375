#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用数据库连接器工厂
支持多种数据库类型，具有泛化能力
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
import importlib

logger = logging.getLogger(__name__)


class DatabaseConnector(ABC):
    """数据库连接器抽象基类"""
    
    @abstractmethod
    def connect(self) -> bool:
        """建立数据库连接"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """断开数据库连接"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """检查连接状态"""
        pass
    
    @abstractmethod
    def run_sql(self, sql: str, params: Optional[tuple] = None) -> Optional[list]:
        """执行SQL查询"""
        pass
    
    @abstractmethod
    def import_database_schema(self, ddl_collection=None, train_method=None) -> bool:
        """导入数据库结构"""
        pass
    
    @abstractmethod
    def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        pass


class ConnectionFactory:
    """数据库连接器工厂"""
    
    def __init__(self):
        self.connectors = {}
        self._register_default_connectors()
    
    def _register_default_connectors(self):
        """注册默认的数据库连接器"""
        try:
            # MySQL连接器
            from .mysql_connector import MySQLConnector
            self.register_connector('mysql', MySQLConnector)
            self.register_connector('mariadb', MySQLConnector)
        except ImportError:
            logger.warning("MySQL连接器不可用")
        
        try:
            # PostgreSQL连接器
            from .postgresql_connector import PostgreSQLConnector
            self.register_connector('postgresql', PostgreSQLConnector)
            self.register_connector('postgres', PostgreSQLConnector)
        except ImportError:
            logger.warning("PostgreSQL连接器不可用")
        
        try:
            # SQLite连接器
            from .sqlite_connector import SQLiteConnector
            self.register_connector('sqlite', SQLiteConnector)
            self.register_connector('sqlite3', SQLiteConnector)
        except ImportError:
            logger.warning("SQLite连接器不可用")
        
        try:
            # Snowflake连接器
            from .snowflake_connector import SnowflakeConnector
            self.register_connector('snowflake', SnowflakeConnector)
        except ImportError:
            logger.warning("Snowflake连接器不可用")
    
    def register_connector(self, database_type: str, connector_class: type):
        """注册数据库连接器"""
        self.connectors[database_type.lower()] = connector_class
        logger.info(f"注册数据库连接器: {database_type} -> {connector_class.__name__}")
    
    def get_connector(self, database_type: str, **kwargs) -> Optional[DatabaseConnector]:
        """获取数据库连接器实例"""
        database_type = database_type.lower()
        
        if database_type not in self.connectors:
            logger.error(f"不支持的数据库类型: {database_type}")
            logger.info(f"支持的数据库类型: {list(self.connectors.keys())}")
            return None
        
        try:
            connector_class = self.connectors[database_type]
            return connector_class(**kwargs)
        except Exception as e:
            logger.error(f"创建数据库连接器失败: {e}")
            return None
    
    def create_connection(self, connection_string: str, **kwargs) -> Optional[DatabaseConnector]:
        """从连接字符串创建数据库连接"""
        try:
            # 解析连接字符串
            db_type, connection_params = self._parse_connection_string(connection_string)
            
            if not db_type:
                logger.error("无法从连接字符串解析数据库类型")
                return None
            
            # 合并参数
            connection_params.update(kwargs)
            
            # 创建连接器
            return self.get_connector(db_type, **connection_params)
            
        except Exception as e:
            logger.error(f"从连接字符串创建连接失败: {e}")
            return None
    
    def _parse_connection_string(self, connection_string: str) -> tuple:
        """解析连接字符串"""
        try:
            if connection_string.startswith('mysql://'):
                # MySQL连接字符串: mysql://user:password@host:port/database
                db_type = 'mysql'
                parts = connection_string[8:].split('@')
                if len(parts) == 2:
                    user_pass = parts[0].split(':')
                    host_port_db = parts[1].split('/')
                    
                    if len(user_pass) == 2 and len(host_port_db) == 2:
                        user, password = user_pass
                        host_port, database = host_port_db
                        host, port = host_port.split(':') if ':' in host_port else (host_port, '3306')
                        
                        return db_type, {
                            'user': user,
                            'password': password,
                            'host': host,
                            'port': int(port),
                            'database': database
                        }
            
            elif connection_string.startswith('postgresql://'):
                # PostgreSQL连接字符串: postgresql://user:password@host:port/database
                db_type = 'postgresql'
                # 类似MySQL的解析逻辑
                return db_type, {}
            
            elif connection_string.startswith('sqlite://'):
                # SQLite连接字符串: sqlite:///path/to/database.db
                db_type = 'sqlite'
                database = connection_string[9:]
                return db_type, {'database': database}
            
            elif connection_string.startswith('snowflake://'):
                # Snowflake连接字符串: snowflake://user:password@account/database/schema
                db_type = 'snowflake'
                # 解析Snowflake特定参数
                return db_type, {}
            
            else:
                logger.warning(f"未知的连接字符串格式: {connection_string}")
                return None, {}
                
        except Exception as e:
            logger.error(f"解析连接字符串失败: {e}")
            return None, {}
    
    def get_supported_databases(self) -> list:
        """获取支持的数据库类型列表"""
        return list(self.connectors.keys())
    
    def test_connection(self, database_type: str, **kwargs) -> bool:
        """测试数据库连接"""
        try:
            connector = self.get_connector(database_type, **kwargs)
            if connector:
                success = connector.connect()
                if success:
                    connector.disconnect()
                    return True
            return False
        except Exception as e:
            logger.error(f"测试连接失败: {e}")
            return False


# 便捷函数
def create_connection(database_type: str, **kwargs) -> Optional[DatabaseConnector]:
    """创建数据库连接的便捷函数"""
    factory = ConnectionFactory()
    return factory.get_connector(database_type, **kwargs)


def create_connection_from_string(connection_string: str, **kwargs) -> Optional[DatabaseConnector]:
    """从连接字符串创建数据库连接的便捷函数"""
    factory = ConnectionFactory()
    return factory.create_connection(connection_string, **kwargs)


def get_supported_databases() -> list:
    """获取支持的数据库类型列表"""
    factory = ConnectionFactory()
    return factory.get_supported_databases()


def test_connection(database_type: str, **kwargs) -> bool:
    """测试数据库连接的便捷函数"""
    factory = ConnectionFactory()
    return factory.test_connection(database_type, **kwargs)
