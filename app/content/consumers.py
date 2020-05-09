import os
import random
import string
import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.db.models import Q
from django.template.loader import render_to_string

from core._tools.choices import FILETYPES_CHOICES
from .models import SharedFile, Comment

class CommentConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print("connected", event)
        id = self.scope['url_route']['kwargs']['id']
        user = self.scope['user']
        shared_file_obj = await self.get_shared_file(user, id)
        self.shared_file_obj = shared_file_obj
        file_page = "thread_{}".format(shared_file_obj.id)
        self.file_page = file_page
        await self.channel_layer.group_add(
            file_page,
            self.channel_name
        )
        await self.send({
            "type":"websocket.accept",
        })
    async def websocket_receive(self, event):
        print("receive", event)
        get_text  = event.get('text',None)
        if get_text is not None:
            loaded_dict_data = json.loads(get_text)
            msg = loaded_dict_data.get('message')
            type_req = loaded_dict_data.get('type')
            total_response = {
                "code": 1,
                "message": '',
                "type": type_req,
            }

            user = self.scope['user']
            if type_req == 'add':
                result_message = await self.add_new_comment(user,msg)
                replace_text = await self.randomString(18)
                _comment_html = "{}".format(render_to_string(
                "pages/files/_include/comment-part/comment-item-main.html",
                {
                    "comment_item": result_message,
                    "replace_text": replace_text,
                }))
                _action_edit_html = "{}".format(render_to_string(
                "pages/files/_include/comment-part/action-part-edit.html",
                {
                    "comment_item": result_message,
                }))
                _action_delete_html = "{}".format(render_to_string(
                "pages/files/_include/comment-part/action-part-delete.html",
                {
                    "comment_item": result_message,
                }))
                total_response = {
                    "code":1,
                    "message":_comment_html,
                    "action_edit_html":_action_edit_html,
                    "action_delete_html":_action_delete_html,
                    "type":type_req,
                    "user":user.username,
                    "author":result_message.shared_file.author.username,
                    "replace_text":replace_text,
                }
            elif type_req == 'edit':

                id = loaded_dict_data.get('id')
                result_message = await self.edit_comment(user,msg,id)
                # _comment_html = "{}".format(result_message.text)
                total_response = {
                    "code":result_message[0],
                    "message":result_message[1],
                    "type":type_req,
                    "id":id,
                }
            elif type_req == 'remove':
                result_message = await self.remove_comment(user,msg)
                if result_message:
                    code = 1
                    message = msg
                else:
                    code = 0
                    message = ''
                total_response = {
                    "code":code,
                    "message":message,
                    "type":type_req,
                }
            await self.channel_layer.group_send(
                self.file_page,
                {
                    "type":"file_comment",
                    "text":json.dumps(total_response)
                }
            )
    async def file_comment(self, event):
        await self.send({
            "type":"websocket.send",
            "text": event['text']
        })
    async def websocket_disconnect(self, event):
        print("disconnected", event)
    async def randomString(self, stringLength=16):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))
    @database_sync_to_async
    def get_shared_file(self, user, id):
        # return SharedFile.objects.get(id=id)
        return SharedFile.objects.filter(id=id).filter(Q(author=user) | Q(user_shared_file__user=user, user_shared_file__permission_type=FILETYPES_CHOICES[2][0])).distinct().get()

    @database_sync_to_async
    def add_new_comment(self,user, text):
        # return SharedFile.objects.get(id=id)
        return Comment.objects.create(user=user,shared_file=self.shared_file_obj,text=text)

    @database_sync_to_async
    def remove_comment(self,user, id):
        # return SharedFile.objects.get(id=id)
        try:
            comment_item = Comment.objects.filter(Q(user=user) | Q(shared_file__author=user)).get(id=id)
            comment_item.delete()
            return True
        except:
            return False

    @database_sync_to_async
    def edit_comment(self,user, text, id):
        # return SharedFile.objects.get(id=id)
        print("*******________________{}".format(id))
        try:
            comment_item = Comment.objects.get(user=user,id=id)
            comment_item.text = text
            comment_item.save()
            return [1,text]
        except:
            return [0,'']

from channels.consumer import AsyncConsumer

class EchoConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        await self.send({
            "type": "websocket.accept",
        })
        await asyncio.sleep(10)

        await self.send({
            "type": "websocket.close",
        })

    async def websocket_receive(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["text"],
        })
    async def websocket_disconnect(self, event):
        print("disconnected", event)