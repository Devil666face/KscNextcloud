import urllib3
import socket
from datetime import datetime
from dataclasses import dataclass
from typing import (
    List,
    Set,
    Union,
)
from KlAkOAPI.ChunkAccessor import KlAkChunkAccessor
from KlAkOAPI.AdmServer import KlAkAdmServer
from KlAkOAPI.HostGroup import KlAkHostGroup


@dataclass
class KscRawData:
    computer_name: str
    ksc_last_date: datetime


class KscServer:
    def __init__(
        self, ip: str, username: str, password: str, port: int = 13299
    ) -> None:
        urllib3.disable_warnings()
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.server_url = f"https://{socket.getfqdn(self.ip)}:{self.port}"
        try:
            self.server = KlAkAdmServer.Create(
                self.server_url,
                self.username,
                self.password,
                verify=False,
            )
        except ConnectionError as ex:
            print(ex)

    def get_host_field(self, fields_to_select: List[str]):
        self.fields_to_select = fields_to_select
        fields_list: List[str] = list()
        str_accessor = (
            KlAkHostGroup(self.server)
            .FindHosts(
                "",
                self.fields_to_select,
                [],
                {"KLGRP_FIND_FROM_CUR_VS_ONLY": False},
                lMaxLifeTime=60 * 60,
            )
            .OutPar("strAccessor")
        )
        chunk_acessor = KlAkChunkAccessor(self.server)
        count = chunk_acessor.GetItemsCount(str_accessor).RetVal()
        for start in range(0, count, 1000):
            chunk = chunk_acessor.GetItemsChunk(str_accessor, start, 1000)
            hosts = chunk.OutPar("pChunk")["KLCSP_ITERATOR_ARRAY"]
            for obj in hosts:
                fields_list.append(
                    [self.get_field(obj, field) for field in self.fields_to_select]
                )
        return fields_list

    def list_of_computer_names(
        self,
        fields_to_select: List[str] = ["KLHST_WKS_DN", "KLHST_WKS_LAST_VISIBLE"],
    ) -> List[KscRawData]:
        fields_list: List[Union[str, datetime]] = self.get_host_field(fields_to_select)
        fields_list_typing: List[KscRawData] = [
            KscRawData(
                computer_name=name_date_for_host[0],
                ksc_last_date=name_date_for_host[1],
            )
            for name_date_for_host in fields_list
        ]
        return fields_list_typing
        # set_host_list: Set[str] = set([host[0] for host in fields_list])
        # return set([host[0] for host in fields_list])

    def get_field(self, obj, field_name: str) -> str | datetime:
        try:
            return obj[field_name]
        except:
            return "-"
