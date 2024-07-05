from DBM.ADBM import AbstractDBManager
import hashlib
import os
from multimethod import multimethod


class UsersManager(AbstractDBManager):
    @multimethod
    def has_status(self, status: str):
        # TODO:
        # Check status using other services

        # return self._is_status_of("user", status)
        pass

    @multimethod
    def has(self, user_name: str, log=False):
        id = self._SELECT("id", "user", "name", user_name)
        if not id:
            return self.logger.log(f"Error: No such user '{user_name}'.", 0) if log else 0
        return id
    
    @multimethod
    def has(self, user_id: int, log=False):
        id = self._SELECT("id", "user", "id", user_id)
        if not id:
            return self.logger.log(f"Error: No such user #{user_id}.", 0) if log else 0
        return id

    def status_of(self, identifier, log=False):
        # TODO:
        # Check status using other services

        # user_id = self.has(identifier, log=log)
        # if not user_id:
        #     return ""
        # return self._status_getter("user", user_id)
        pass

    def get_info(self, identifier):
        # TODO:
        # get created_at from other services
        # get status from other services
        user_info_dict = {}

        user_id = self.has(identifier)
        with self.db as (conn, cursor):
            cursor.execute("""
                SELECT name, updated_at, n_samples_collected
                FROM "user"
                WHERE id = %s
            """, (user_id,))
            user_data = cursor.fetchone()

        if user_data:
            user_info_dict['id'] = user_id
            user_info_dict['name'] = user_data[0]
            # user_info_dict['status'] = self.status_of(identifier)
            # user_info_dict['created_at'] = user_data[1].astimezone().isoformat()
            user_info_dict['updated_at'] = user_data[1].astimezone().isoformat()
            user_info_dict['n_samples_collected'] = user_data[2]
        return user_info_dict

    def get_all(self):
        return self._all_getter("name", "user")

    # @multimethod
    # TODO: fetching created users from auth_service
    # def new(self, user_name: str, password: str, log=False):
    #     if self.has(user_name, log=log):
    #         return False
    #     if not self._validate_user_name(user_name, log=log):
    #         return False
    #     if not self._validate_password(password, user_name, log=log):
    #         return False
        
    #     password_hash, salt = self._hash_and_salt(password)

    #     with self.db as (conn, cursor):
    #         cursor.execute("""
    #             INSERT INTO "user"
    #             (name, password_hash, password_salt)
    #             VALUES (%s, %s, %s)
    #             RETURNING id
    #         """, (user_name, password_hash, salt))
    #         user_id = cursor.fetchone()[0]
    #         conn.commit()
    #     log and self.logger.log(f"Info : User #{user_id} '{user_name}' has been created", user_id)
    #     return user_id


    # @multimethod
    # def rename(self, user_identifier, new_user_name: str, log=False):
    #     TODO: call other services to apply changes there too
    #     user_id =  self.has(user_identifier, log=log)
    #     if not user_id:
    #         return self.logger.log(f"Error: Can't change user_name of a nonexisting user '{user_identifier}'.", "") if log else ""
        
    #     new_username_id = self.has(new_user_name)
    #     if user_id==new_username_id:
    #         return new_user_name

    #     if new_username_id:
    #         return self.logger.log(f"Error: Can't change user_name for user #{user_id} to '{new_user_name}' - the name is taken.", "") if log else ""

    #     if not self._validate_user_name(new_user_name, log=log):
    #         return ""
        
    #     with self.db as (conn, cursor):
    #         cursor.execute('UPDATE "user" SET name = %s WHERE id = %s', (new_user_name, user_id))
    #         conn.commit()
            
    #     log and self.logger.log(f"Info : User #{user_id} changed name to '{new_user_name}'.", new_user_name)
    #     return new_user_name
