import os
import json

from DE_Lib.Utils import Generic

gen = Generic.GENERIC()

class INFORMIX:
    def __init__(self):
        self._connection_is_valid = None
        self._nome_database = None
        self._cnn = None
        self.__database_error = None

    # ----------------------------------------------------------------
    # Falta tudo (Instalar driver ODBC) Maquina local não permite
    def Connect(self, string_connect: dict):
        msg, result = None, None
        try:
            pass
            self._connection_is_valid = True
            self._nome_database = gen.nvl(string_connect["database"], "")
            self._cnn = result
            self.__database_error = f"""{json.dumps(string_connect, indent=4).replace(string_connect["password"], "******")}\nConexao bem sucedida!"""
        except Exception as error:
            msg = f"""{json.dumps(string_connect, indent=4).replace(string_connect["password"], "******")}\nFalha ao tentar se conectar com o banco de dados ORACLE\nException Error: {error} """
            result = msg
            self._connection_is_valid = False
            self.__database_error = msg
        finally:
            return result

    @property
    def CONNECTION(self):
        return self._cnn

    @property
    def CONNECTION_VALID(self):
        return self._connection_is_valid

    @property
    def NOME_DATABASE(self):
        return self._nome_database.upper()

    @property
    def DATABASE_ERROR(self):
        return self.__database_error