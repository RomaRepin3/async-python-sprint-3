from typing import Dict

from data_transfer_objects.request_dto import RequestDto


class RequestDtoRowMapper:

    @staticmethod
    async def get_from_dict(request_data: Dict[str, str]) -> RequestDto:
        return RequestDto(
            client_name=request_data['client_name'],
            endpoint=request_data['endpoint'],
            message=request_data['message'],
            recipient=request_data['recipient'],
            chat_name=request_data['chat_name'],
        )
