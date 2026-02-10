import asyncio
import os
import re
import uuid
from datetime import datetime, timedelta, timezone
from ftplib import all_errors
from pathlib import Path

import aiohttp
import httpx
import requests
from dotenv import load_dotenv

load_dotenv()

eboda_url_api = os.getenv("url_api_eboda")
ecnaheb_url_api = os.getenv("url_api_ecnaheb")


class Behance:
    headers = {
        "Content-Type": "application/json",
        "Origin": f"https://auth.{eboda_url_api}",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Trailer/93.3.3570.29",
        "cookie": "fg=2F3YLG4BFLM5ADEKFAQVIHAACI======;bcp=c2dbb12f-87db-4cca-83de-e27ac3455de8;gk_suid=15619008;gki=feature_primary_nav_blue_susi:false,; relay=3aec9da6-6de2-45be-9e8d-96550d9604d4; kndctr_9E1005A551ED61CA0A490D45_AdobeOrg_identity=CiYyMDMzMTMyOTQ3MzI3OTYwMDUzMjY5NTE1MTczMTE5MzE2OTMxN1ITCPeM9ITDMxABGAEqBElSTDEwAPAB94z0hMMz; AMCV_9E1005A551ED61CA0A490D45%40AdobeOrg=MCMID|20331329473279600532695151731193169317; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Feb+06+2026+11%3A26%3A31+GMT%2B0700+(Indochina+Time)&version=202501.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=e3330136-aa71-488f-99fd-f95aa87803c6&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0&AwaitingReconsent=false; RDC=AYoekcfGwQMjcls455yX5r_DSxs8g7JpJDYDUT8YcxGY_SBShaJ-yimeK5qM8YF5180RHRAYJe3gU1DPXYCXsHewnR8IMsAYal3sQD9Cv5zmpTapmriKSjFWC3s8CQ3MQQ74XMPp8LiEhwHI3ZhbzOR3qn8K; filter-profile-map-permanent=AZvgFe3dqnCPUi34U6xh9zZU6OsQ3yZong_A70EOuYF_nOp18Y8m9Piv4eO0gR-VwlOD71-BgGYpF892Csfhhk0AHEIt9GeOVs7lIn9gnDMKbJ1SBIVa9XHtHbM8gC7qTs8RrZTN3xBL6LictuhuQqq9ia8vbIWy2GhbCkQiYil2xbOv_JtvrxmOrcefO-0E7_7NmMOujT677qd4XS4iqockGwSLBSyurZIFiKT4553PrZ_VX9VB2p1WAFofzGlu6A; gpv=Account:IMS:WelcomeBack:AdobeID:OnLoad; kndctr_9E1005A551ED61CA0A490D45_AdobeOrg_cluster=irl1",
        "X-DEBUG-ID": "3aec9da6-6de2-45be-9e8d-96550d9604d4",
        "X-IMS-CLIENTID": "BehanceWebSusi1",
        "X-BCP": "c2dbb12f-87db-4cca-83de-e27ac3455de8",
        "X-NewRelic-ID": "VgUFVldbGwsFU1BRDwUBVw==",
        "X-Requested-With": "XMLHttpRequest",
    }
    username = None
    password = None
    authorization_bearer = None

    def __init__(self, username, password):
        self.username = username
        self.password = password

    async def login(self):
        url = f"https://auth.{eboda_url_api}/signin/v1/passkey"
        response = requests.post(url, headers=self.headers)
        verification_token = response.headers.get("X-Identity-Verification-Token")
        if response.status_code == 200 and verification_token:
            url = f"https://auth.{eboda_url_api}/signin/v2/authenticationstate?purpose=multiFactorAuthentication"
            payload = {
                "extraPbaChecks": False,
                "pbaPolicy": None,
                "username": self.username,
                "usernameType": "EMAIL",
                "accountType": "individual",
                "deviceInfo": {
                    "lsId": "801c318f-a082-4a41-b9e2-0e517b76d978",
                    "hdId": None,
                },
            }
            response = requests.post(
                url,
                headers={
                    **self.headers,
                    "X-Identity-Verification-Token": verification_token,
                },
                json=payload,
            )
            if response.status_code == 201:
                url = f"https://auth.{eboda_url_api}/signin/v3/challenges?purpose=multiFactorAuthentication"
                authentication_state_encrypted = response.headers.get(
                    "x-ims-authentication-state-encrypted"
                )
                if authentication_state_encrypted:
                    response = requests.get(
                        url,
                        headers={
                            **self.headers,
                            "X-Identity-Verification-Token": verification_token,
                            "x-ims-authentication-state-encrypted": authentication_state_encrypted,
                        },
                        json=payload,
                    )
                    authentication_state_encrypted = response.headers.get(
                        "x-ims-authentication-state-encrypted"
                    )
                    if response.status_code == 200 and authentication_state_encrypted:
                        url = f"https://auth.{eboda_url_api}/signin/v2/tokens?credential=password"
                        payload = {
                            "username": self.username,
                            "usernameType": "EMAIL",
                            "password": self.password,
                            "accountType": "individual",
                            "rememberMe": True,
                        }
                        response = requests.post(
                            url,
                            headers={
                                **self.headers,
                                "X-Identity-Verification-Token": verification_token,
                                "x-ims-authentication-state-encrypted": authentication_state_encrypted,
                            },
                            json=payload,
                        )
                        if response.status_code == 200:
                            jsonData = response.json()
                            if jsonData and "token" in jsonData:
                                token = jsonData["token"]
                                url = (
                                    f"https://auth.{eboda_url_api}/signin/v1/ims/tokens"
                                )
                                payload = {
                                    "rememberMe": True,
                                    "reauthenticate": None,
                                }
                                response = requests.post(
                                    url,
                                    headers={
                                        **self.headers,
                                        "X-Identity-Verification-Token": verification_token,
                                        "x-ims-authentication-state-encrypted": authentication_state_encrypted,
                                        "authorization": f"Bearer {token}",
                                    },
                                    json=payload,
                                )
                                jsonData = response.json()
                                token = jsonData["token"]
                                url = (
                                    f"https://adobeid-na1.{eboda_url_api}/ims/fromSusi"
                                )
                                payload = {
                                    "remember_me": True,
                                    "token": token,
                                    "client_id": "BehanceWebSusi1",
                                    "scope": "AdobeID,openid,gnav,sao.cce_private,creative_cloud,creative_sdk,be.pro2.external_client,additional_info.roles,ims_cai.verifiedId.read,ims_cai.social.read,ims_cai.social.workplace.read",
                                    "state": {
                                        "ac": "{ecnaheb_url_api}",
                                        "csrf": "24cb3172-129c-4eae-8566-5e25a1b0d931",
                                        "timestamp": "1770351292198",
                                        "context": {"intent": "signIn"},
                                        "jslibver": "v2-v0.49.0-12-gfb1792a",
                                        "nonce": "2271927464218502",
                                    },
                                    "flow": "signIn",
                                    "use_ms_for_expiry": True,
                                    "code_challenge_method": "plain",
                                    "response_type": "token",
                                    "idp_flow_type": "login",
                                    "locale": "en_US",
                                    "dctx_id": "v:2,s,179a5130-6796-11f0-8b7e-43217feca831",
                                    "redirect_uri": f"https://www.{ecnaheb_url_api}/?isa0=1#old_hash=&from_ims=true&client_id=BehanceWebSusi1&api=authorize&scope=AdobeID,openid,gnav,sao.cce_private,creative_cloud,creative_sdk,be.pro2.external_client,additional_info.roles,ims_cai.verifiedId.read,ims_cai.social.read,ims_cai.social.workplace.read",
                                    "callback": f"https://ims-na1.adobelogin.com/ims/adobeid/BehanceWebSusi1/AdobeID/token?redirect_uri=https%3A%2F%2Fwww.{ecnaheb_url_api}%2F%3Fisa0%3D1%23old_hash%3D%26from_ims%3Dtrue%26client_id%3DBehanceWebSusi1%26api%3Dauthorize%26scope%3DAdobeID%2Copenid%2Cgnav%2Csao.cce_private%2Ccreative_cloud%2Ccreative_sdk%2Cbe.pro2.external_client%2Cadditional_info.roles%2Cims_cai.verifiedId.read%2Cims_cai.social.read%2Cims_cai.social.workplace.read&state=%7B%22ac%22%3A%22{ecnaheb_url_api}%22%2C%22csrf%22%3A%2224cb3172-129c-4eae-8566-5e25a1b0d931%22%2C%22timestamp%22%3A%221770351292198%22%2C%22context%22%3A%7B%22intent%22%3A%22signIn%22%7D%2C%22jslibver%22%3A%22v2-v0.49.0-12-gfb1792a%22%2C%22nonce%22%3A%222271927464218502%22%7D&code_challenge_method=plain&use_ms_for_expiry=true",
                                }
                                response = requests.post(
                                    url,
                                    headers={
                                        **self.headers,
                                        "content-type": "application/x-www-form-urlencoded",
                                    },
                                    data=payload,
                                )

                                if response.status_code == 200:
                                    textContent = response.text
                                    found = re.search(
                                        r".*#access_token\=(.*?)\&.*",
                                        textContent,
                                    )
                                    if found:
                                        self.headers = {
                                            **self.headers,
                                            "cookie": f"bcp=c2dbb12f-87db-4cca-83de-e27ac3455de8; gk_suid=15619008; gki=feature_primary_nav_blue_susi:false,; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Feb+06+2026+16%3A38%3A12+GMT%2B0700+(Indochina+Time)&version=202501.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=959b7036-81ad-47bd-a5df-2f23f0279a56&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0&intType=2; OptanonAlertBoxClosed=2026-02-06T06:20:14.390Z; dialog_dismissals=new_embed_type%3Bannouncement_307%3Bwork_boost_upsell_banner;iat0={found.group(1)}",
                                        }
                                        self.authorization_bearer = found.group(1)
                                        return self.headers

        # timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None)
        # async with aiohttp.ClientSession(timeout=timeout) as session:
        #     async with session.post(url, headers=self.headers, ssl=False) as response:
        #         verification_token = response.headers.get(
        #             "X-Identity-Verification-Token"
        #         )
        #         if response.status == 200 and verification_token:
        #             url = f"https://auth.{eboda_url_api}/signin/v2/authenticationstate?purpose=multiFactorAuthentication"
        #             payload = {
        #                 "extraPbaChecks": False,
        #                 "pbaPolicy": None,
        #                 "username": self.username,
        #                 "usernameType": "EMAIL",
        #                 "accountType": "individual",
        #                 "deviceInfo": {
        #                     "lsId": "801c318f-a082-4a41-b9e2-0e517b76d978",
        #                     "hdId": None,
        #                 },
        #             }
        #             async with session.post(
        #                 url,
        #                 headers={
        #                     **self.headers,
        #                     "X-Identity-Verification-Token": verification_token,
        #                 },
        #                 json=payload,
        #             ) as response:
        #                 if response.status == 201:
        #                     url = f"https://auth.{eboda_url_api}/signin/v3/challenges?purpose=multiFactorAuthentication"
        #                     authentication_state_encrypted = response.headers.get(
        #                         "x-ims-authentication-state-encrypted"
        #                     )
        #                     if authentication_state_encrypted:
        #                         async with session.get(
        #                             url,
        #                             headers={
        #                                 **self.headers,
        #                                 "X-Identity-Verification-Token": verification_token,
        #                                 "x-ims-authentication-state-encrypted": authentication_state_encrypted,
        #                             },
        #                             json=payload,
        #                         ) as response:
        #                             authentication_state_encrypted = (
        #                                 response.headers.get(
        #                                     "x-ims-authentication-state-encrypted"
        #                                 )
        #                             )
        #                             if (
        #                                 response.status == 200
        #                                 and authentication_state_encrypted
        #                             ):
        #                                 url = f"https://auth.{eboda_url_api}/signin/v2/tokens?credential=password"
        #                                 payload = {
        #                                     "username": self.username,
        #                                     "usernameType": "EMAIL",
        #                                     "password": self.password,
        #                                     "accountType": "individual",
        #                                     "rememberMe": True,
        #                                 }
        #                                 async with session.post(
        #                                     url,
        #                                     headers={
        #                                         **self.headers,
        #                                         "X-Identity-Verification-Token": verification_token,
        #                                         "x-ims-authentication-state-encrypted": authentication_state_encrypted,
        #                                     },
        #                                     json=payload,
        #                                 ) as response:
        #                                     if response.status == 200:
        #                                         jsonData = await response.json()
        #                                         token = jsonData["token"]
        #                                         url = f"https://auth.{eboda_url_api}/signin/v1/ims/tokens"
        #                                         payload = {
        #                                             "rememberMe": True,
        #                                             "reauthenticate": None,
        #                                         }
        #                                         async with session.post(
        #                                             url,
        #                                             headers={
        #                                                 **self.headers,
        #                                                 "X-Identity-Verification-Token": verification_token,
        #                                                 "x-ims-authentication-state-encrypted": authentication_state_encrypted,
        #                                                 "authorization": f"Bearer {token}",
        #                                             },
        #                                             json=payload,
        #                                         ) as response:
        #                                             jsonData = await response.json()
        #                                             token = jsonData["token"]
        #                                             url = f"https://adobeid-na1.{eboda_url_api}/ims/fromSusi"
        #                                             payload = {
        #                                                 "remember_me": True,
        #                                                 "token": token,
        #                                                 "client_id": "BehanceWebSusi1",
        #                                                 "scope": "AdobeID,openid,gnav,sao.cce_private,creative_cloud,creative_sdk,be.pro2.external_client,additional_info.roles,ims_cai.verifiedId.read,ims_cai.social.read,ims_cai.social.workplace.read",
        #                                                 "state": {
        #                                                     "ac": "{ecnaheb_url_api}",
        #                                                     "csrf": "24cb3172-129c-4eae-8566-5e25a1b0d931",
        #                                                     "timestamp": "1770351292198",
        #                                                     "context": {
        #                                                         "intent": "signIn"
        #                                                     },
        #                                                     "jslibver": "v2-v0.49.0-12-gfb1792a",
        #                                                     "nonce": "2271927464218502",
        #                                                 },
        #                                                 "flow": "signIn",
        #                                                 "use_ms_for_expiry": True,
        #                                                 "code_challenge_method": "plain",
        #                                                 "response_type": "token",
        #                                                 "idp_flow_type": "login",
        #                                                 "locale": "en_US",
        #                                                 "dctx_id": "v:2,s,179a5130-6796-11f0-8b7e-43217feca831",
        #                                                 "redirect_uri": f"https://www.{ecnaheb_url_api}/?isa0=1#old_hash=&from_ims=true&client_id=BehanceWebSusi1&api=authorize&scope=AdobeID,openid,gnav,sao.cce_private,creative_cloud,creative_sdk,be.pro2.external_client,additional_info.roles,ims_cai.verifiedId.read,ims_cai.social.read,ims_cai.social.workplace.read",
        #                                                 "callback": f"https://ims-na1.adobelogin.com/ims/adobeid/BehanceWebSusi1/AdobeID/token?redirect_uri=https%3A%2F%2Fwww.{ecnaheb_url_api}%2F%3Fisa0%3D1%23old_hash%3D%26from_ims%3Dtrue%26client_id%3DBehanceWebSusi1%26api%3Dauthorize%26scope%3DAdobeID%2Copenid%2Cgnav%2Csao.cce_private%2Ccreative_cloud%2Ccreative_sdk%2Cbe.pro2.external_client%2Cadditional_info.roles%2Cims_cai.verifiedId.read%2Cims_cai.social.read%2Cims_cai.social.workplace.read&state=%7B%22ac%22%3A%22{ecnaheb_url_api}%22%2C%22csrf%22%3A%2224cb3172-129c-4eae-8566-5e25a1b0d931%22%2C%22timestamp%22%3A%221770351292198%22%2C%22context%22%3A%7B%22intent%22%3A%22signIn%22%7D%2C%22jslibver%22%3A%22v2-v0.49.0-12-gfb1792a%22%2C%22nonce%22%3A%222271927464218502%22%7D&code_challenge_method=plain&use_ms_for_expiry=true",
        #                                             }
        #                                             async with session.post(
        #                                                 url,
        #                                                 headers={
        #                                                     **self.headers,
        #                                                     "content-type": "application/x-www-form-urlencoded",
        #                                                 },
        #                                                 data=payload,
        #                                             ) as response:
        #                                                 if response.status == 200:
        #                                                     textContent = (
        #                                                         await response.text()
        #                                                     )
        #                                                     found = re.search(
        #                                                         r".*#access_token\=(.*?)\&.*",
        #                                                         textContent,
        #                                                     )
        #                                                     if found:
        #                                                         self.headers = {
        #                                                             **self.headers,
        #                                                             "cookie": f"bcp=c2dbb12f-87db-4cca-83de-e27ac3455de8; gk_suid=15619008; gki=feature_primary_nav_blue_susi:false,; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Feb+06+2026+16%3A38%3A12+GMT%2B0700+(Indochina+Time)&version=202501.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=959b7036-81ad-47bd-a5df-2f23f0279a56&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0003%3A0%2CC0004%3A0&intType=2; OptanonAlertBoxClosed=2026-02-06T06:20:14.390Z; dialog_dismissals=new_embed_type%3Bannouncement_307%3Bwork_boost_upsell_banner;iat0={found.group(1)}",
        #                                                         }
        #                                                         self.authorization_bearer = found.group(
        #                                                             1
        #                                                         )
        #                                                         return self.headers

    async def uploadImage(self, project_id: int, file_path):
        file_path = Path(file_path)
        file_name = file_path.name
        suffix = file_path.suffix[1:]

        now_gmt = datetime.now(timezone.utc)
        time_formatted = now_gmt.strftime("%a, %d %b %Y %H:%M:%S GMT")
        file_uuid = f"{uuid.uuid4()}.{suffix}"
        url = f"https://www.{ecnaheb_url_api}/v2/project/editor/sign_request"
        payload = {
            "headers": f"POST\n\nimage/png\n\nx-amz-acl:private\nx-amz-date:{time_formatted}\nx-amz-meta-qqfilename:{file_name}\n/be-network-tmp-prod-ue1-a/{file_uuid}?uploads"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                jsonData = response.json()
                signatureFirst = jsonData["signature"]
                if signatureFirst:
                    url = f"https://s3.amazonaws.com/be-network-tmp-prod-ue1-a/{file_uuid}?uploads="
                    response = requests.post(
                        url,
                        headers={
                            **self.headers,
                            "Authorization": f"AWS AKIARCNKPTSWXRTDDYM4:{signatureFirst}",
                            "x-amz-acl": "private",
                            "x-amz-meta-qqfilename": file_name,
                            "x-amz-date": time_formatted,
                            "content-type": f"image/{suffix}",
                        },
                    )
                    if response.status_code == 200:
                        text_content = response.text
                        upload_id = re.search(
                            r".*<UploadId>(.*?)</UploadId>", text_content
                        ).group(1)
                        url = f"https://www.{ecnaheb_url_api}/v2/project/editor/sign_request"
                        payload = {
                            "headers": f"PUT\n\n\n\nx-amz-date:{time_formatted}\n/be-network-tmp-prod-ue1-a/{file_uuid}?partNumber=1&uploadId={upload_id}"
                        }
                        response = await client.post(
                            url,
                            headers={
                                **self.headers,
                                "x-amz-acl": "private",
                                "x-amz-meta-qqfilename": file_name,
                                "x-amz-date": time_formatted,
                                "content-type": "application/json; charset=utf-8",
                            },
                            json=payload,
                        )
                        if response.status_code == 200:
                            jsonData = response.json()
                            signature = jsonData["signature"]
                            if signature:
                                with open(file_path, "rb") as f:
                                    file_bytes = f.read()
                                    url = f"https://s3.amazonaws.com/be-network-tmp-prod-ue1-a/{file_uuid}?partNumber=1&uploadId={upload_id}"
                                    response = await client.put(
                                        url,
                                        headers={
                                            "Authorization": f"AWS AKIARCNKPTSWXRTDDYM4:{signature}",
                                            "x-amz-date": time_formatted,
                                        },
                                        data=file_bytes,
                                    )
                                    if response.status_code != 200:
                                        raise Exception(
                                            f"Failed to upload file: {response.status_code}"
                                        )
                                    if response.status_code == 200:
                                        etag = response.headers.get("ETag")
                                        url = f"https://www.{ecnaheb_url_api}/v2/project/editor/sign_request"
                                        payload = {
                                            "headers": f"POST\n\napplication/xml; charset=UTF-8\n\nx-amz-date:{time_formatted}\n/be-network-tmp-prod-ue1-a/{file_uuid}?uploadId={upload_id}"
                                        }
                                        response = await client.post(
                                            url,
                                            headers={
                                                **self.headers,
                                                "x-amz-acl": "private",
                                                "x-amz-meta-qqfilename": file_name,
                                                "x-amz-date": time_formatted,
                                                "content-type": "application/json; charset=utf-8",
                                            },
                                            json=payload,
                                        )
                                        if response.status_code == 200:
                                            jsonData = response.json()
                                            signature = jsonData["signature"]
                                            payload = f"<CompleteMultipartUpload><Part><PartNumber>1</PartNumber><ETag>{etag}</ETag></Part></CompleteMultipartUpload>"
                                            url = f"https://s3.amazonaws.com/be-network-tmp-prod-ue1-a/{file_uuid}?uploadId={upload_id}"
                                            response = requests.post(
                                                url,
                                                headers={
                                                    **self.headers,
                                                    "Authorization": f"AWS AKIARCNKPTSWXRTDDYM4:{signature}",
                                                    "x-amz-date": time_formatted,
                                                    "content-type": "application/xml; charset=UTF-8",
                                                },
                                                data=payload,
                                            )
                                            if response.status_code == 200:
                                                url = f"https://www.{ecnaheb_url_api}/v3/graphql"
                                                payload = {
                                                    "query": "\n  query ProjectEditorPage($projectId: ProjectId!) {\n    siteConfig {\n      ...siteConfigFields\n    }\n    project(id: $projectId) {\n      ...projectEditorFields\n    }\n  }\n\n  \n  fragment projectEditorFields on Project {\n    id\n    agencies {\n      ...projectTagFields\n    }\n    allModules {\n      __typename\n      ... on AudioModule {\n        ...audioModuleFields\n      }\n      ... on EmbedModule {\n        ...embedModuleFields\n      }\n      ... on ImageModule {\n        ...imageModuleFields\n      }\n      ... on MediaCollectionModule {\n        ...mediaCollectionModuleFields\n      }\n      ... on TextModule {\n        ...textModuleFields\n      }\n      ... on VideoModule {\n        ...videoModuleFields\n      }\n    }\n    brands {\n      ...projectTagFields\n    }\n    colors {\n      r\n      g\n      b\n    }\n    covers {\n      ...projectCoverFields\n    }\n    coverData {\n      coverScale\n      coverX\n      coverY\n    }\n    createdOn\n    creatorId\n    credits {\n      displayName\n      images {\n        size_50 {\n          url\n        }\n      }\n      id\n    }\n    description\n    editorVersion\n    features {\n      featuredOn\n      name\n      ribbon {\n        image\n        image2x\n      }\n      url\n    }\n    fields {\n      id\n      label\n      slug\n      url\n    }\n    creator {\n      isFollowing\n      hasAllowEmbeds\n      availabilityInfo {\n        isAvailableFreelance\n      }\n      isMessageButtonVisible\n    }\n    hasMatureContent\n    hasPassword\n    isBoosted\n    activeBoost {\n      id\n      user {\n        id\n        username\n        displayName\n      }\n    }\n    isCommentingAllowed\n    isFounder\n    isMatureReviewSubmitted\n    isMonaReported\n    isPrivate\n    isPublished\n    isPinnedToSubscriptionOverview\n    linkedAssetsCount\n    linkedAssets {\n      ...sourceLinkFields\n    }\n    sourceFiles {\n      ...sourceFileWithRenditionsFields\n    }\n    license {\n      description\n      label\n      license\n      id\n    }\n    matureAccess\n    name\n    networks {\n      id\n      icon\n      key\n      name\n      visible\n    }\n    owners {\n      ...OwnerFields\n      firstName\n      images {\n        size_50 {\n          url\n        }\n      }\n      hasAllowEmbeds\n    }\n    pendingCoowners {\n      displayName\n      id\n    }\n    publishedOn\n    publishStatus\n    premium\n    privacyLevel\n    projectCTA {\n      ctaType\n      link {\n        url\n        title\n        description\n      }\n      isDefaultCTA\n    }\n    scheduledOn\n    schools {\n      ...projectTagFields\n    }\n    slug\n    stats {\n      appreciations {\n        all\n      }\n      comments {\n        all\n      }\n      views {\n        all\n      }\n    }\n    styles {\n      ...projectStylesFields\n    }\n    tags {\n      ...projectTagFields\n    }\n    teams {\n      ...projectTeamFields\n    }\n    tools {\n      ...projectToolFields\n    }\n    url\n  }\n  \n  fragment OwnerFields on User {\n    displayName\n    hasPremiumAccess\n    id\n    isFollowing\n    isProfileOwner\n    location\n    locationUrl\n    url\n    username\n    isMessageButtonVisible\n    availabilityInfo {\n      availabilityTimeline\n      isAvailableFullTime\n      isAvailableFreelance\n      hiringTimeline {\n        key\n        label\n      }\n    }\n    creatorPro {\n      isActive\n      initialSubscriptionDate\n    }\n  }\n\n\n  \n  fragment siteConfigFields on SiteConfig {\n    projectEditorConfig {\n      allowedExtensions {\n        audio\n        image\n        video\n      }\n      allowedSourceFileMimeTypes\n      canvasMaxWidth\n      canvasPadding\n      embedTransformsEndpoint\n      fontConfig {\n        orderedFonts {\n          css\n          label\n          userTypekit\n          regular\n          value\n        }\n      }\n      hasCCV\n      hasLightroom\n      lightroomEndpoint\n      sizeLimits {\n        audio\n        image\n        video\n      }\n      sourceFileSizeLimit\n      substanceUploadEndpoint\n      threeDAssetTypes {\n        substanceAtlas\n        substanceDecal\n        substanceMaterial\n        substanceModel\n      }\n      threeDFileExtensionToAssetTypeMap {\n        fbx\n        glb\n        sbsar\n      }\n    }\n    uploader {\n      requestAccessKey\n      requestEndpoint\n      signatureEndpoint\n      unixTimestamp\n    }\n  }\n\n  \n  fragment audioModuleFields on AudioModule {\n    alignment\n    captionAlignment\n    caption\n    embed\n    fullBleed\n    id\n    isDoneProcessing\n    projectId\n    status\n  }\n\n  \n  fragment embedModuleFields on EmbedModule {\n    alignment\n    caption\n    captionAlignment\n    captionPlain\n    fluidEmbed\n    embedModuleFullBleed: fullBleed\n    height\n    id\n    originalEmbed\n    originalHeight\n    originalWidth\n    width\n    widthUnit\n  }\n\n  \n  fragment imageModuleFields on ImageModule {\n    alignment\n    altText\n    altTextForEditor\n    caiData\n    hasCaiData\n    caption\n    captionAlignment\n    captionPlain\n    flexHeight\n    flexWidth\n    fullBleed\n    height\n    id\n    isCaiVersion1\n    projectId\n    src\n    tags\n    width\n    imageSizes {\n      ...imageSizesFields\n    }\n  }\n\n  \n  fragment textModuleFields on TextModule {\n    id\n    fullBleed\n    alignment\n    captionAlignment\n    text\n    textPlain\n    projectId\n  }\n\n  \n  fragment videoModuleFields on VideoModule {\n    alignment\n    captionAlignment\n    caption\n    embed\n    fullBleed\n    height\n    id\n    isDoneProcessing\n    src\n    videoData {\n      renditions {\n        url\n      }\n      status\n    }\n    width\n  }\n\n  \n  fragment imageSizesFields on ProjectModuleImageSizes {\n    size_disp {\n      height\n      url\n      width\n    }\n    size_fs {\n      height\n      url\n      width\n    }\n    size_max_1200 {\n      height\n      url\n      width\n    }\n    size_original {\n      height\n      url\n      width\n    }\n    size_1400 {\n      height\n      url\n      width\n    }\n    size_1400_opt_1 {\n      height\n      url\n      width\n    }\n    size_2800_opt_1 {\n      height\n      url\n      width\n    }\n    size_max_3840 {\n      height\n      url\n      width\n    }\n    allAvailable {\n      height\n      url\n      width\n      type\n    }\n  }\n\n  \n  fragment mediaCollectionModuleFields on MediaCollectionModule {\n    alignment\n    captionAlignment\n    captionPlain\n    collectionType\n    components {\n      filename\n      flexHeight\n      flexWidth\n      height\n      id\n      imageSizes {\n        size_disp {\n          height\n          url\n          width\n        }\n        size_fs {\n          height\n          url\n          width\n        }\n        size_max_1200 {\n          height\n          url\n          width\n        }\n        size_1400_opt_1 {\n          height\n          url\n          width\n        }\n        size_2800_opt_1 {\n          height\n          url\n          width\n        }\n      }\n      position\n      width\n    }\n    id\n    fullBleed\n    sortType\n  }\n\n  \n  fragment projectCoverFields on ProjectCoverImageSizes {\n    size_original {\n      url\n    }\n    size_115 {\n      url\n    }\n    size_202 {\n      url\n    }\n    size_230 {\n      url\n    }\n    size_404 {\n      url\n    }\n    size_808 {\n      url\n    }\n    size_max_808 {\n      url\n    }\n  }\n\n  \n  fragment projectStylesFields on ProjectStyle {\n    background {\n      color\n    }\n    divider {\n      borderStyle\n      borderWidth\n      display\n      fontSize\n      height\n      lineHeight\n      margin\n      position\n      top\n    }\n    spacing {\n      moduleBottomMargin\n      projectTopMargin\n    }\n  }\n\n  \n  fragment projectTeamFields on TeamItem {\n    displayName\n    id\n    imageSizes {\n      size_115 {\n        height\n        url\n        width\n      }\n      size_138 {\n        height\n        url\n        width\n      }\n      size_276 {\n        height\n        url\n        width\n      }\n    }\n    locationDisplay\n    slug\n    url\n  }\n\n  \n  fragment projectToolFields on Tool {\n    approved\n    backgroundColor\n    backgroundImage {\n      size_original {\n        height\n        url\n        width\n      }\n      size_max_808 {\n        height\n        url\n        width\n      }\n      size_404 {\n        height\n        url\n        width\n      }\n    }\n    category\n    categoryLabel\n    categoryId\n    id\n    synonym {\n      authenticated\n      downloadUrl\n      galleryUrl\n      iconUrl\n      iconUrl2x\n      name\n      synonymId\n      tagId\n      title\n      type\n      url\n    }\n    title\n    url\n  }\n\n  \n  fragment projectTagFields on Tag {\n    category\n    id\n    title\n  }\n\n  \n  fragment sourceFileWithRenditionsFields on SourceFile {\n    __typename\n    sourceFileId\n    projectId\n    userId\n    title\n    assetId\n    renditionUrl\n    mimeType\n    size\n    category\n    licenseType\n    unitAmount\n    currency\n    tier\n    hidden\n    extension\n    hasUserPurchased\n    description\n    renditions {\n      etag\n      fileName\n      id\n      md5\n      mimeType\n      size\n      srcUrl\n    }\n    cover {\n      coverUrl\n      coverX\n      coverY\n      coverScale\n    }\n  }\n\n  \n  fragment sourceLinkFields on LinkedAsset {\n    __typename\n    name\n    premium\n    url\n    category\n    licenseType\n  }\n\n",
                                                    "variables": {
                                                        "projectId": project_id
                                                    },
                                                }
                                                response = await client.post(
                                                    url,
                                                    headers={
                                                        **self.headers,
                                                        "authorization": f"Bearer {self.authorization_bearer}",
                                                        "content-type": "application/json",
                                                    },
                                                    json=payload,
                                                )
                                                if response.status_code == 200:
                                                    jsonData = response.json()
                                                    if jsonData:
                                                        all_modules = jsonData["data"][
                                                            "project"
                                                        ]["allModules"]
                                                        all_modules_mapped = list(
                                                            map(
                                                                lambda item: {
                                                                    "imageModule": {
                                                                        **{
                                                                            k: v
                                                                            for k, v in item.items()
                                                                            if k
                                                                            in [
                                                                                "alignment",
                                                                                "altText",
                                                                                "caption",
                                                                                "captionAlignment",
                                                                                "fullBleed",
                                                                                "id",
                                                                                "tags",
                                                                            ]
                                                                        },
                                                                        "fullBleed": "NO",
                                                                    }
                                                                },
                                                                all_modules,
                                                            )
                                                        )
                                                        all_modules_mapped.append(
                                                            {
                                                                "imageModule": {
                                                                    "alignment": "center",
                                                                    "caption": "",
                                                                    "fullBleed": "NO",
                                                                    "captionAlignment": "left",
                                                                    "id": -1,
                                                                    "srcUrl": f"https://s3.amazonaws.com/be-network-tmp-prod-ue1-a/{file_uuid}",
                                                                }
                                                            }
                                                        )
                                                        payload = {
                                                            "query": "\n        mutation updateProject($projectId: Int!, $params: UpdateProjectParams!) {\n          updateProject(projectId: $projectId, params: $params) {\n            ... on UpdateProjectInvalidInputError {\n              __typename\n              descriptionError\n              errorMessage\n              titleError\n              passwordError\n              scheduledOnError\n              tagsErrors {\n                errorMessage\n              }\n              modulesErrors {\n                errorMessage\n              }\n            }\n            ... on Project {\n              ...projectEditorFields\n            }\n          }\n        }\n        \n  fragment projectEditorFields on Project {\n    id\n    agencies {\n      ...projectTagFields\n    }\n    allModules {\n      __typename\n      ... on AudioModule {\n        ...audioModuleFields\n      }\n      ... on EmbedModule {\n        ...embedModuleFields\n      }\n      ... on ImageModule {\n        ...imageModuleFields\n      }\n      ... on MediaCollectionModule {\n        ...mediaCollectionModuleFields\n      }\n      ... on TextModule {\n        ...textModuleFields\n      }\n      ... on VideoModule {\n        ...videoModuleFields\n      }\n    }\n    brands {\n      ...projectTagFields\n    }\n    colors {\n      r\n      g\n      b\n    }\n    covers {\n      ...projectCoverFields\n    }\n    coverData {\n      coverScale\n      coverX\n      coverY\n    }\n    createdOn\n    creatorId\n    credits {\n      displayName\n      images {\n        size_50 {\n          url\n        }\n      }\n      id\n    }\n    description\n    editorVersion\n    features {\n      featuredOn\n      name\n      ribbon {\n        image\n        image2x\n      }\n      url\n    }\n    fields {\n      id\n      label\n      slug\n      url\n    }\n    creator {\n      isFollowing\n      hasAllowEmbeds\n      availabilityInfo {\n        isAvailableFreelance\n      }\n      isMessageButtonVisible\n    }\n    hasMatureContent\n    hasPassword\n    isBoosted\n    activeBoost {\n      id\n      user {\n        id\n        username\n        displayName\n      }\n    }\n    isCommentingAllowed\n    isFounder\n    isMatureReviewSubmitted\n    isMonaReported\n    isPrivate\n    isPublished\n    isPinnedToSubscriptionOverview\n    linkedAssetsCount\n    linkedAssets {\n      ...sourceLinkFields\n    }\n    sourceFiles {\n      ...sourceFileWithRenditionsFields\n    }\n    license {\n      description\n      label\n      license\n      id\n    }\n    matureAccess\n    name\n    networks {\n      id\n      icon\n      key\n      name\n      visible\n    }\n    owners {\n      ...OwnerFields\n      firstName\n      images {\n        size_50 {\n          url\n        }\n      }\n      hasAllowEmbeds\n    }\n    pendingCoowners {\n      displayName\n      id\n    }\n    publishedOn\n    publishStatus\n    premium\n    privacyLevel\n    projectCTA {\n      ctaType\n      link {\n        url\n        title\n        description\n      }\n      isDefaultCTA\n    }\n    scheduledOn\n    schools {\n      ...projectTagFields\n    }\n    slug\n    stats {\n      appreciations {\n        all\n      }\n      comments {\n        all\n      }\n      views {\n        all\n      }\n    }\n    styles {\n      ...projectStylesFields\n    }\n    tags {\n      ...projectTagFields\n    }\n    teams {\n      ...projectTeamFields\n    }\n    tools {\n      ...projectToolFields\n    }\n    url\n  }\n  \n  fragment OwnerFields on User {\n    displayName\n    hasPremiumAccess\n    id\n    isFollowing\n    isProfileOwner\n    location\n    locationUrl\n    url\n    username\n    isMessageButtonVisible\n    availabilityInfo {\n      availabilityTimeline\n      isAvailableFullTime\n      isAvailableFreelance\n      hiringTimeline {\n        key\n        label\n      }\n    }\n    creatorPro {\n      isActive\n      initialSubscriptionDate\n    }\n  }\n\n\n        \n  fragment audioModuleFields on AudioModule {\n    alignment\n    captionAlignment\n    caption\n    embed\n    fullBleed\n    id\n    isDoneProcessing\n    projectId\n    status\n  }\n\n        \n  fragment embedModuleFields on EmbedModule {\n    alignment\n    caption\n    captionAlignment\n    captionPlain\n    fluidEmbed\n    embedModuleFullBleed: fullBleed\n    height\n    id\n    originalEmbed\n    originalHeight\n    originalWidth\n    width\n    widthUnit\n  }\n\n        \n  fragment imageModuleFields on ImageModule {\n    alignment\n    altText\n    altTextForEditor\n    caiData\n    hasCaiData\n    caption\n    captionAlignment\n    captionPlain\n    flexHeight\n    flexWidth\n    fullBleed\n    height\n    id\n    isCaiVersion1\n    projectId\n    src\n    tags\n    width\n    imageSizes {\n      ...imageSizesFields\n    }\n  }\n\n        \n  fragment textModuleFields on TextModule {\n    id\n    fullBleed\n    alignment\n    captionAlignment\n    text\n    textPlain\n    projectId\n  }\n\n        \n  fragment videoModuleFields on VideoModule {\n    alignment\n    captionAlignment\n    caption\n    embed\n    fullBleed\n    height\n    id\n    isDoneProcessing\n    src\n    videoData {\n      renditions {\n        url\n      }\n      status\n    }\n    width\n  }\n\n        \n  fragment imageSizesFields on ProjectModuleImageSizes {\n    size_disp {\n      height\n      url\n      width\n    }\n    size_fs {\n      height\n      url\n      width\n    }\n    size_max_1200 {\n      height\n      url\n      width\n    }\n    size_original {\n      height\n      url\n      width\n    }\n    size_1400 {\n      height\n      url\n      width\n    }\n    size_1400_opt_1 {\n      height\n      url\n      width\n    }\n    size_2800_opt_1 {\n      height\n      url\n      width\n    }\n    size_max_3840 {\n      height\n      url\n      width\n    }\n    allAvailable {\n      height\n      url\n      width\n      type\n    }\n  }\n\n        \n  fragment mediaCollectionModuleFields on MediaCollectionModule {\n    alignment\n    captionAlignment\n    captionPlain\n    collectionType\n    components {\n      filename\n      flexHeight\n      flexWidth\n      height\n      id\n      imageSizes {\n        size_disp {\n          height\n          url\n          width\n        }\n        size_fs {\n          height\n          url\n          width\n        }\n        size_max_1200 {\n          height\n          url\n          width\n        }\n        size_1400_opt_1 {\n          height\n          url\n          width\n        }\n        size_2800_opt_1 {\n          height\n          url\n          width\n        }\n      }\n      position\n      width\n    }\n    id\n    fullBleed\n    sortType\n  }\n\n        \n  fragment projectCoverFields on ProjectCoverImageSizes {\n    size_original {\n      url\n    }\n    size_115 {\n      url\n    }\n    size_202 {\n      url\n    }\n    size_230 {\n      url\n    }\n    size_404 {\n      url\n    }\n    size_808 {\n      url\n    }\n    size_max_808 {\n      url\n    }\n  }\n\n        \n  fragment projectStylesFields on ProjectStyle {\n    background {\n      color\n    }\n    divider {\n      borderStyle\n      borderWidth\n      display\n      fontSize\n      height\n      lineHeight\n      margin\n      position\n      top\n    }\n    spacing {\n      moduleBottomMargin\n      projectTopMargin\n    }\n  }\n\n        \n  fragment projectTeamFields on TeamItem {\n    displayName\n    id\n    imageSizes {\n      size_115 {\n        height\n        url\n        width\n      }\n      size_138 {\n        height\n        url\n        width\n      }\n      size_276 {\n        height\n        url\n        width\n      }\n    }\n    locationDisplay\n    slug\n    url\n  }\n\n        \n  fragment projectToolFields on Tool {\n    approved\n    backgroundColor\n    backgroundImage {\n      size_original {\n        height\n        url\n        width\n      }\n      size_max_808 {\n        height\n        url\n        width\n      }\n      size_404 {\n        height\n        url\n        width\n      }\n    }\n    category\n    categoryLabel\n    categoryId\n    id\n    synonym {\n      authenticated\n      downloadUrl\n      galleryUrl\n      iconUrl\n      iconUrl2x\n      name\n      synonymId\n      tagId\n      title\n      type\n      url\n    }\n    title\n    url\n  }\n\n        \n  fragment projectTagFields on Tag {\n    category\n    id\n    title\n  }\n\n        \n  fragment sourceFileWithRenditionsFields on SourceFile {\n    __typename\n    sourceFileId\n    projectId\n    userId\n    title\n    assetId\n    renditionUrl\n    mimeType\n    size\n    category\n    licenseType\n    unitAmount\n    currency\n    tier\n    hidden\n    extension\n    hasUserPurchased\n    description\n    renditions {\n      etag\n      fileName\n      id\n      md5\n      mimeType\n      size\n      srcUrl\n    }\n    cover {\n      coverUrl\n      coverX\n      coverY\n      coverScale\n    }\n  }\n\n        \n  fragment sourceLinkFields on LinkedAsset {\n    __typename\n    name\n    premium\n    url\n    category\n    licenseType\n  }\n\n      ",
                                                            "variables": {
                                                                "projectId": 243693391,
                                                                "params": {
                                                                    "agencies": "",
                                                                    "assets": [],
                                                                    "backgroundColor": "FFFFFF",
                                                                    "brands": "",
                                                                    "captionStyles": {
                                                                        "color": "a4a4a4",
                                                                        "fontFamily": "helvetica,arial,sans-serif",
                                                                        "fontSize": 14,
                                                                        "fontStyle": "italic",
                                                                        "fontWeight": "normal",
                                                                        "lineHeight": 1.4,
                                                                        "textAlign": "left",
                                                                        "textDecoration": "none",
                                                                        "textTransform": "none",
                                                                    },
                                                                    "canvasTopMargin": 80,
                                                                    "commentsStatus": "ALLOWED",
                                                                    "coowners": "2044610771",
                                                                    "creativeFields": "",
                                                                    "credits": "",
                                                                    "description": "",
                                                                    "license": "NO_USE",
                                                                    "linkStyles": {
                                                                        "color": "1769FF",
                                                                        "fontFamily": "helvetica,arial,sans-serif",
                                                                        "fontSize": 20,
                                                                        "fontStyle": "normal",
                                                                        "fontWeight": "normal",
                                                                        "lineHeight": 1.4,
                                                                        "textAlign": "left",
                                                                        "textDecoration": "none",
                                                                        "textTransform": "none",
                                                                    },
                                                                    "matureContentStatus": "OFF",
                                                                    "modules": [
                                                                        {
                                                                            "imageModule": {
                                                                                "id": 1406309813,
                                                                                "alignment": "center",
                                                                                "captionAlignment": "left",
                                                                                "fullBleed": "NO",
                                                                                "caption": "",
                                                                                "tags": [],
                                                                                "altText": "Image may contain: screenshot",
                                                                            }
                                                                        },
                                                                        {
                                                                            "imageModule": {
                                                                                "id": 1406309815,
                                                                                "alignment": "center",
                                                                                "captionAlignment": "left",
                                                                                "fullBleed": "NO",
                                                                                "caption": "",
                                                                                "tags": [],
                                                                                "altText": "Image may contain: screenshot",
                                                                            }
                                                                        },
                                                                        {
                                                                            "imageModule": {
                                                                                "id": 1406309817,
                                                                                "alignment": "center",
                                                                                "captionAlignment": "left",
                                                                                "fullBleed": "NO",
                                                                                "caption": "",
                                                                                "tags": [],
                                                                                "altText": "Image may contain: screenshot",
                                                                            }
                                                                        },
                                                                        {
                                                                            "imageModule": {
                                                                                "id": -1,
                                                                                "alignment": "center",
                                                                                "captionAlignment": "left",
                                                                                "fullBleed": "NO",
                                                                                "srcUrl": "https://s3.amazonaws.com/be-network-tmp-prod-ue1-a/582302bc-ec29-4b76-9842-02193e6558ef.png",
                                                                                "caption": "",
                                                                            }
                                                                        },
                                                                    ],
                                                                    "moduleBottomMargin": 60,
                                                                    "paragraphStyles": {
                                                                        "color": "696969",
                                                                        "fontFamily": "helvetica,arial,sans-serif",
                                                                        "fontSize": 20,
                                                                        "fontStyle": "normal",
                                                                        "fontWeight": "normal",
                                                                        "lineHeight": 1.4,
                                                                        "textAlign": "left",
                                                                        "textDecoration": "none",
                                                                        "textTransform": "none",
                                                                    },
                                                                    "publishStatus": "DRAFT",
                                                                    "schools": "",
                                                                    "subTitleStyles": {
                                                                        "color": "a4a4a4",
                                                                        "fontFamily": "helvetica,arial,sans-serif",
                                                                        "fontSize": 20,
                                                                        "fontStyle": "normal",
                                                                        "fontWeight": "normal",
                                                                        "lineHeight": 1.4,
                                                                        "textAlign": "left",
                                                                        "textDecoration": "none",
                                                                        "textTransform": "none",
                                                                    },
                                                                    "tags": "",
                                                                    "teams": "",
                                                                    "titleStyles": {
                                                                        "color": "191919",
                                                                        "fontFamily": "helvetica,arial,sans-serif",
                                                                        "fontSize": 36,
                                                                        "fontStyle": "normal",
                                                                        "fontWeight": "bold",
                                                                        "lineHeight": 1.1,
                                                                        "textAlign": "left",
                                                                        "textDecoration": "none",
                                                                        "textTransform": "none",
                                                                    },
                                                                    "tools": "",
                                                                    "visibleNetworkIds": "0",
                                                                },
                                                            },
                                                        }

                                                        response = await client.post(
                                                            url,
                                                            headers={
                                                                **self.headers,
                                                                "authorization": f"Bearer {self.authorization_bearer}",
                                                                "content-type": "application/json",
                                                            },
                                                            json={
                                                                **payload,
                                                                "variables": {
                                                                    **payload[
                                                                        "variables"
                                                                    ],
                                                                    "params": {
                                                                        **payload[
                                                                            "variables"
                                                                        ]["params"],
                                                                        "modules": all_modules_mapped,
                                                                    },
                                                                },
                                                            },
                                                        )
                                                        if response.status_code == 200:
                                                            json_data = response.json()
                                                            if (
                                                                json_data
                                                                and "data" in json_data
                                                                and "updateProject"
                                                                in json_data["data"]
                                                            ):
                                                                print(
                                                                    f"{project_id} updated successfully"
                                                                )
                                                                return json_data[
                                                                    "data"
                                                                ]["updateProject"][
                                                                    "allModules"
                                                                ]
                                                        raise Exception(
                                                            "Failed to update project"
                                                        )

        # async with aiohttp.ClientSession() as session:
        #     async with session.post(
        #         url, headers=self.headers, json=payload
        #     ) as response:
        #         if response.status == 200:
        #             jsonData = await response.json()
        #             signatureFirst = jsonData["signature"]
        #             if signatureFirst:
        #                 url = f"https://s3.amazonaws.com/be-network-tmp-prod-ue1-a/{file_uuid}?uploads="
        #                 async with session.post(
        #                     url,
        #                     headers={
        #                         **self.headers,
        #                         "Authorization": f"AWS AKIARCNKPTSWXRTDDYM4:{signatureFirst}",
        #                         "x-amz-acl": "private",
        #                         "x-amz-meta-qqfilename": file_name,
        #                         "x-amz-date": time_formatted,
        #                         "content-type": f"image/{suffix}",
        #                     },
        #                 ) as response:
        #                     if response.status == 200:
        #                         text_content = await response.text()
        #                         upload_id = re.search(
        #                             r".*<UploadId>(.*?)</UploadId>", text_content
        #                         ).group(1)
        #                         url = f"https://www.{ecnaheb_url_api}/v2/project/editor/sign_request"
        #                         payload = {
        #                             "headers": f"PUT\n\n\n\nx-amz-date:{time_formatted}\n/be-network-tmp-prod-ue1-a/{file_uuid}?partNumber=1&uploadId={upload_id}"
        #                         }
        #                         async with session.post(
        #                             url,
        #                             headers={
        #                                 **self.headers,
        #                                 "x-amz-acl": "private",
        #                                 "x-amz-meta-qqfilename": file_name,
        #                                 "x-amz-date": time_formatted,
        #                                 "content-type": "application/json; charset=utf-8",
        #                             },
        #                             json=payload,
        #                         ) as response:
        #                             if response.status == 200:
        #                                 jsonData = await response.json()
        #                                 signature = jsonData["signature"]
        #                                 if signature:
        #                                     with open(file_path, "rb") as f:
        #                                         file_bytes = f.read()
        #                                         url = f"https://s3.amazonaws.com/be-network-tmp-prod-ue1-a/{file_uuid}?partNumber=1&uploadId={upload_id}"
        #                                         req = requests.put(
        #                                             url,
        #                                             headers={
        #                                                 "Authorization": f"AWS AKIARCNKPTSWXRTDDYM4:{signature}",
        #                                                 "x-amz-date": time_formatted,
        #                                             },
        #                                             data=file_bytes,
        #                                         )
        #                                         if req.status_code != 200:
        #                                             raise Exception(
        #                                                 f"Failed to upload file: {req.status_code}"
        #                                             )
        #                                         if req.status_code == 200:
        #                                             etag = req.headers.get("ETag")
        #                                             url = f"https://www.{ecnaheb_url_api}/v2/project/editor/sign_request"
        #                                             payload = {
        #                                                 "headers": f"POST\n\napplication/xml; charset=UTF-8\n\nx-amz-date:{time_formatted}\n/be-network-tmp-prod-ue1-a/{file_uuid}?uploadId={upload_id}"
        #                                             }
        #                                             async with session.post(
        #                                                 url,
        #                                                 headers={
        #                                                     **self.headers,
        #                                                     "x-amz-acl": "private",
        #                                                     "x-amz-meta-qqfilename": file_name,
        #                                                     "x-amz-date": time_formatted,
        #                                                     "content-type": "application/json; charset=utf-8",
        #                                                 },
        #                                                 json=payload,
        #                                             ) as response:
        #                                                 if response.status == 200:
        #                                                     jsonData = (
        #                                                         await response.json()
        #                                                     )
        #                                                     signature = jsonData[
        #                                                         "signature"
        #                                                     ]
        #                                                     payload = f"<CompleteMultipartUpload><Part><PartNumber>1</PartNumber><ETag>{etag}</ETag></Part></CompleteMultipartUpload>"
        #                                                     url = f"https://s3.amazonaws.com/be-network-tmp-prod-ue1-a/{file_uuid}?uploadId={upload_id}"
        #                                                     async with session.post(
        #                                                         url,
        #                                                         headers={
        #                                                             **self.headers,
        #                                                             "Authorization": f"AWS AKIARCNKPTSWXRTDDYM4:{signature}",
        #                                                             "x-amz-date": time_formatted,
        #                                                             "content-type": "application/xml; charset=UTF-8",
        #                                                         },
        #                                                         data=payload,
        #                                                     ) as response:
        #                                                         if (
        #                                                             response.status
        #                                                             == 200
        #                                                         ):
        #                                                             url = f"https://www.{ecnaheb_url_api}/v3/graphql"
        #                                                             payload = {
        #                                                                 "query": "\n  query ProjectEditorPage($projectId: ProjectId!) {\n    siteConfig {\n      ...siteConfigFields\n    }\n    project(id: $projectId) {\n      ...projectEditorFields\n    }\n  }\n\n  \n  fragment projectEditorFields on Project {\n    id\n    agencies {\n      ...projectTagFields\n    }\n    allModules {\n      __typename\n      ... on AudioModule {\n        ...audioModuleFields\n      }\n      ... on EmbedModule {\n        ...embedModuleFields\n      }\n      ... on ImageModule {\n        ...imageModuleFields\n      }\n      ... on MediaCollectionModule {\n        ...mediaCollectionModuleFields\n      }\n      ... on TextModule {\n        ...textModuleFields\n      }\n      ... on VideoModule {\n        ...videoModuleFields\n      }\n    }\n    brands {\n      ...projectTagFields\n    }\n    colors {\n      r\n      g\n      b\n    }\n    covers {\n      ...projectCoverFields\n    }\n    coverData {\n      coverScale\n      coverX\n      coverY\n    }\n    createdOn\n    creatorId\n    credits {\n      displayName\n      images {\n        size_50 {\n          url\n        }\n      }\n      id\n    }\n    description\n    editorVersion\n    features {\n      featuredOn\n      name\n      ribbon {\n        image\n        image2x\n      }\n      url\n    }\n    fields {\n      id\n      label\n      slug\n      url\n    }\n    creator {\n      isFollowing\n      hasAllowEmbeds\n      availabilityInfo {\n        isAvailableFreelance\n      }\n      isMessageButtonVisible\n    }\n    hasMatureContent\n    hasPassword\n    isBoosted\n    activeBoost {\n      id\n      user {\n        id\n        username\n        displayName\n      }\n    }\n    isCommentingAllowed\n    isFounder\n    isMatureReviewSubmitted\n    isMonaReported\n    isPrivate\n    isPublished\n    isPinnedToSubscriptionOverview\n    linkedAssetsCount\n    linkedAssets {\n      ...sourceLinkFields\n    }\n    sourceFiles {\n      ...sourceFileWithRenditionsFields\n    }\n    license {\n      description\n      label\n      license\n      id\n    }\n    matureAccess\n    name\n    networks {\n      id\n      icon\n      key\n      name\n      visible\n    }\n    owners {\n      ...OwnerFields\n      firstName\n      images {\n        size_50 {\n          url\n        }\n      }\n      hasAllowEmbeds\n    }\n    pendingCoowners {\n      displayName\n      id\n    }\n    publishedOn\n    publishStatus\n    premium\n    privacyLevel\n    projectCTA {\n      ctaType\n      link {\n        url\n        title\n        description\n      }\n      isDefaultCTA\n    }\n    scheduledOn\n    schools {\n      ...projectTagFields\n    }\n    slug\n    stats {\n      appreciations {\n        all\n      }\n      comments {\n        all\n      }\n      views {\n        all\n      }\n    }\n    styles {\n      ...projectStylesFields\n    }\n    tags {\n      ...projectTagFields\n    }\n    teams {\n      ...projectTeamFields\n    }\n    tools {\n      ...projectToolFields\n    }\n    url\n  }\n  \n  fragment OwnerFields on User {\n    displayName\n    hasPremiumAccess\n    id\n    isFollowing\n    isProfileOwner\n    location\n    locationUrl\n    url\n    username\n    isMessageButtonVisible\n    availabilityInfo {\n      availabilityTimeline\n      isAvailableFullTime\n      isAvailableFreelance\n      hiringTimeline {\n        key\n        label\n      }\n    }\n    creatorPro {\n      isActive\n      initialSubscriptionDate\n    }\n  }\n\n\n  \n  fragment siteConfigFields on SiteConfig {\n    projectEditorConfig {\n      allowedExtensions {\n        audio\n        image\n        video\n      }\n      allowedSourceFileMimeTypes\n      canvasMaxWidth\n      canvasPadding\n      embedTransformsEndpoint\n      fontConfig {\n        orderedFonts {\n          css\n          label\n          userTypekit\n          regular\n          value\n        }\n      }\n      hasCCV\n      hasLightroom\n      lightroomEndpoint\n      sizeLimits {\n        audio\n        image\n        video\n      }\n      sourceFileSizeLimit\n      substanceUploadEndpoint\n      threeDAssetTypes {\n        substanceAtlas\n        substanceDecal\n        substanceMaterial\n        substanceModel\n      }\n      threeDFileExtensionToAssetTypeMap {\n        fbx\n        glb\n        sbsar\n      }\n    }\n    uploader {\n      requestAccessKey\n      requestEndpoint\n      signatureEndpoint\n      unixTimestamp\n    }\n  }\n\n  \n  fragment audioModuleFields on AudioModule {\n    alignment\n    captionAlignment\n    caption\n    embed\n    fullBleed\n    id\n    isDoneProcessing\n    projectId\n    status\n  }\n\n  \n  fragment embedModuleFields on EmbedModule {\n    alignment\n    caption\n    captionAlignment\n    captionPlain\n    fluidEmbed\n    embedModuleFullBleed: fullBleed\n    height\n    id\n    originalEmbed\n    originalHeight\n    originalWidth\n    width\n    widthUnit\n  }\n\n  \n  fragment imageModuleFields on ImageModule {\n    alignment\n    altText\n    altTextForEditor\n    caiData\n    hasCaiData\n    caption\n    captionAlignment\n    captionPlain\n    flexHeight\n    flexWidth\n    fullBleed\n    height\n    id\n    isCaiVersion1\n    projectId\n    src\n    tags\n    width\n    imageSizes {\n      ...imageSizesFields\n    }\n  }\n\n  \n  fragment textModuleFields on TextModule {\n    id\n    fullBleed\n    alignment\n    captionAlignment\n    text\n    textPlain\n    projectId\n  }\n\n  \n  fragment videoModuleFields on VideoModule {\n    alignment\n    captionAlignment\n    caption\n    embed\n    fullBleed\n    height\n    id\n    isDoneProcessing\n    src\n    videoData {\n      renditions {\n        url\n      }\n      status\n    }\n    width\n  }\n\n  \n  fragment imageSizesFields on ProjectModuleImageSizes {\n    size_disp {\n      height\n      url\n      width\n    }\n    size_fs {\n      height\n      url\n      width\n    }\n    size_max_1200 {\n      height\n      url\n      width\n    }\n    size_original {\n      height\n      url\n      width\n    }\n    size_1400 {\n      height\n      url\n      width\n    }\n    size_1400_opt_1 {\n      height\n      url\n      width\n    }\n    size_2800_opt_1 {\n      height\n      url\n      width\n    }\n    size_max_3840 {\n      height\n      url\n      width\n    }\n    allAvailable {\n      height\n      url\n      width\n      type\n    }\n  }\n\n  \n  fragment mediaCollectionModuleFields on MediaCollectionModule {\n    alignment\n    captionAlignment\n    captionPlain\n    collectionType\n    components {\n      filename\n      flexHeight\n      flexWidth\n      height\n      id\n      imageSizes {\n        size_disp {\n          height\n          url\n          width\n        }\n        size_fs {\n          height\n          url\n          width\n        }\n        size_max_1200 {\n          height\n          url\n          width\n        }\n        size_1400_opt_1 {\n          height\n          url\n          width\n        }\n        size_2800_opt_1 {\n          height\n          url\n          width\n        }\n      }\n      position\n      width\n    }\n    id\n    fullBleed\n    sortType\n  }\n\n  \n  fragment projectCoverFields on ProjectCoverImageSizes {\n    size_original {\n      url\n    }\n    size_115 {\n      url\n    }\n    size_202 {\n      url\n    }\n    size_230 {\n      url\n    }\n    size_404 {\n      url\n    }\n    size_808 {\n      url\n    }\n    size_max_808 {\n      url\n    }\n  }\n\n  \n  fragment projectStylesFields on ProjectStyle {\n    background {\n      color\n    }\n    divider {\n      borderStyle\n      borderWidth\n      display\n      fontSize\n      height\n      lineHeight\n      margin\n      position\n      top\n    }\n    spacing {\n      moduleBottomMargin\n      projectTopMargin\n    }\n  }\n\n  \n  fragment projectTeamFields on TeamItem {\n    displayName\n    id\n    imageSizes {\n      size_115 {\n        height\n        url\n        width\n      }\n      size_138 {\n        height\n        url\n        width\n      }\n      size_276 {\n        height\n        url\n        width\n      }\n    }\n    locationDisplay\n    slug\n    url\n  }\n\n  \n  fragment projectToolFields on Tool {\n    approved\n    backgroundColor\n    backgroundImage {\n      size_original {\n        height\n        url\n        width\n      }\n      size_max_808 {\n        height\n        url\n        width\n      }\n      size_404 {\n        height\n        url\n        width\n      }\n    }\n    category\n    categoryLabel\n    categoryId\n    id\n    synonym {\n      authenticated\n      downloadUrl\n      galleryUrl\n      iconUrl\n      iconUrl2x\n      name\n      synonymId\n      tagId\n      title\n      type\n      url\n    }\n    title\n    url\n  }\n\n  \n  fragment projectTagFields on Tag {\n    category\n    id\n    title\n  }\n\n  \n  fragment sourceFileWithRenditionsFields on SourceFile {\n    __typename\n    sourceFileId\n    projectId\n    userId\n    title\n    assetId\n    renditionUrl\n    mimeType\n    size\n    category\n    licenseType\n    unitAmount\n    currency\n    tier\n    hidden\n    extension\n    hasUserPurchased\n    description\n    renditions {\n      etag\n      fileName\n      id\n      md5\n      mimeType\n      size\n      srcUrl\n    }\n    cover {\n      coverUrl\n      coverX\n      coverY\n      coverScale\n    }\n  }\n\n  \n  fragment sourceLinkFields on LinkedAsset {\n    __typename\n    name\n    premium\n    url\n    category\n    licenseType\n  }\n\n",
        #                                                                 "variables": {
        #                                                                     "projectId": project_id
        #                                                                 },
        #                                                             }
        #                                                             async with (
        #                                                                 session.post(
        #                                                                     url,
        #                                                                     headers={
        #                                                                         **self.headers,
        #                                                                         "authorization": f"Bearer {self.authorization_bearer}",
        #                                                                         "content-type": "application/json",
        #                                                                     },
        #                                                                     json=payload,
        #                                                                 ) as response
        #                                                             ):
        #                                                                 if (
        #                                                                     response.status
        #                                                                     == 200
        #                                                                 ):
        #                                                                     jsonData = await response.json()
        #                                                                     if jsonData:
        #                                                                         all_modules = jsonData[
        #                                                                             "data"
        #                                                                         ][
        #                                                                             "project"
        #                                                                         ][
        #                                                                             "allModules"
        #                                                                         ]
        #                                                                         all_modules_mapped = list(
        #                                                                             map(
        #                                                                                 lambda item: {
        #                                                                                     "imageModule": {
        #                                                                                         **{
        #                                                                                             k: v
        #                                                                                             for k, v in item.items()
        #                                                                                             if k
        #                                                                                             in [
        #                                                                                                 "alignment",
        #                                                                                                 "altText",
        #                                                                                                 "caption",
        #                                                                                                 "captionAlignment",
        #                                                                                                 "fullBleed",
        #                                                                                                 "id",
        #                                                                                                 "tags",
        #                                                                                             ]
        #                                                                                         },
        #                                                                                         "fullBleed": "NO",
        #                                                                                     }
        #                                                                                 },
        #                                                                                 all_modules,
        #                                                                             )
        #                                                                         )
        #                                                                         all_modules_mapped.append(
        #                                                                             {
        #                                                                                 "imageModule": {
        #                                                                                     "alignment": "center",
        #                                                                                     "caption": "",
        #                                                                                     "fullBleed": "NO",
        #                                                                                     "captionAlignment": "left",
        #                                                                                     "id": -1,
        #                                                                                     "srcUrl": f"https://s3.amazonaws.com/be-network-tmp-prod-ue1-a/{file_uuid}",
        #                                                                                 }
        #                                                                             }
        #                                                                         )
        #                                                                         payload = {
        #                                                                             "query": "\n        mutation updateProject($projectId: Int!, $params: UpdateProjectParams!) {\n          updateProject(projectId: $projectId, params: $params) {\n            ... on UpdateProjectInvalidInputError {\n              __typename\n              descriptionError\n              errorMessage\n              titleError\n              passwordError\n              scheduledOnError\n              tagsErrors {\n                errorMessage\n              }\n              modulesErrors {\n                errorMessage\n              }\n            }\n            ... on Project {\n              ...projectEditorFields\n            }\n          }\n        }\n        \n  fragment projectEditorFields on Project {\n    id\n    agencies {\n      ...projectTagFields\n    }\n    allModules {\n      __typename\n      ... on AudioModule {\n        ...audioModuleFields\n      }\n      ... on EmbedModule {\n        ...embedModuleFields\n      }\n      ... on ImageModule {\n        ...imageModuleFields\n      }\n      ... on MediaCollectionModule {\n        ...mediaCollectionModuleFields\n      }\n      ... on TextModule {\n        ...textModuleFields\n      }\n      ... on VideoModule {\n        ...videoModuleFields\n      }\n    }\n    brands {\n      ...projectTagFields\n    }\n    colors {\n      r\n      g\n      b\n    }\n    covers {\n      ...projectCoverFields\n    }\n    coverData {\n      coverScale\n      coverX\n      coverY\n    }\n    createdOn\n    creatorId\n    credits {\n      displayName\n      images {\n        size_50 {\n          url\n        }\n      }\n      id\n    }\n    description\n    editorVersion\n    features {\n      featuredOn\n      name\n      ribbon {\n        image\n        image2x\n      }\n      url\n    }\n    fields {\n      id\n      label\n      slug\n      url\n    }\n    creator {\n      isFollowing\n      hasAllowEmbeds\n      availabilityInfo {\n        isAvailableFreelance\n      }\n      isMessageButtonVisible\n    }\n    hasMatureContent\n    hasPassword\n    isBoosted\n    activeBoost {\n      id\n      user {\n        id\n        username\n        displayName\n      }\n    }\n    isCommentingAllowed\n    isFounder\n    isMatureReviewSubmitted\n    isMonaReported\n    isPrivate\n    isPublished\n    isPinnedToSubscriptionOverview\n    linkedAssetsCount\n    linkedAssets {\n      ...sourceLinkFields\n    }\n    sourceFiles {\n      ...sourceFileWithRenditionsFields\n    }\n    license {\n      description\n      label\n      license\n      id\n    }\n    matureAccess\n    name\n    networks {\n      id\n      icon\n      key\n      name\n      visible\n    }\n    owners {\n      ...OwnerFields\n      firstName\n      images {\n        size_50 {\n          url\n        }\n      }\n      hasAllowEmbeds\n    }\n    pendingCoowners {\n      displayName\n      id\n    }\n    publishedOn\n    publishStatus\n    premium\n    privacyLevel\n    projectCTA {\n      ctaType\n      link {\n        url\n        title\n        description\n      }\n      isDefaultCTA\n    }\n    scheduledOn\n    schools {\n      ...projectTagFields\n    }\n    slug\n    stats {\n      appreciations {\n        all\n      }\n      comments {\n        all\n      }\n      views {\n        all\n      }\n    }\n    styles {\n      ...projectStylesFields\n    }\n    tags {\n      ...projectTagFields\n    }\n    teams {\n      ...projectTeamFields\n    }\n    tools {\n      ...projectToolFields\n    }\n    url\n  }\n  \n  fragment OwnerFields on User {\n    displayName\n    hasPremiumAccess\n    id\n    isFollowing\n    isProfileOwner\n    location\n    locationUrl\n    url\n    username\n    isMessageButtonVisible\n    availabilityInfo {\n      availabilityTimeline\n      isAvailableFullTime\n      isAvailableFreelance\n      hiringTimeline {\n        key\n        label\n      }\n    }\n    creatorPro {\n      isActive\n      initialSubscriptionDate\n    }\n  }\n\n\n        \n  fragment audioModuleFields on AudioModule {\n    alignment\n    captionAlignment\n    caption\n    embed\n    fullBleed\n    id\n    isDoneProcessing\n    projectId\n    status\n  }\n\n        \n  fragment embedModuleFields on EmbedModule {\n    alignment\n    caption\n    captionAlignment\n    captionPlain\n    fluidEmbed\n    embedModuleFullBleed: fullBleed\n    height\n    id\n    originalEmbed\n    originalHeight\n    originalWidth\n    width\n    widthUnit\n  }\n\n        \n  fragment imageModuleFields on ImageModule {\n    alignment\n    altText\n    altTextForEditor\n    caiData\n    hasCaiData\n    caption\n    captionAlignment\n    captionPlain\n    flexHeight\n    flexWidth\n    fullBleed\n    height\n    id\n    isCaiVersion1\n    projectId\n    src\n    tags\n    width\n    imageSizes {\n      ...imageSizesFields\n    }\n  }\n\n        \n  fragment textModuleFields on TextModule {\n    id\n    fullBleed\n    alignment\n    captionAlignment\n    text\n    textPlain\n    projectId\n  }\n\n        \n  fragment videoModuleFields on VideoModule {\n    alignment\n    captionAlignment\n    caption\n    embed\n    fullBleed\n    height\n    id\n    isDoneProcessing\n    src\n    videoData {\n      renditions {\n        url\n      }\n      status\n    }\n    width\n  }\n\n        \n  fragment imageSizesFields on ProjectModuleImageSizes {\n    size_disp {\n      height\n      url\n      width\n    }\n    size_fs {\n      height\n      url\n      width\n    }\n    size_max_1200 {\n      height\n      url\n      width\n    }\n    size_original {\n      height\n      url\n      width\n    }\n    size_1400 {\n      height\n      url\n      width\n    }\n    size_1400_opt_1 {\n      height\n      url\n      width\n    }\n    size_2800_opt_1 {\n      height\n      url\n      width\n    }\n    size_max_3840 {\n      height\n      url\n      width\n    }\n    allAvailable {\n      height\n      url\n      width\n      type\n    }\n  }\n\n        \n  fragment mediaCollectionModuleFields on MediaCollectionModule {\n    alignment\n    captionAlignment\n    captionPlain\n    collectionType\n    components {\n      filename\n      flexHeight\n      flexWidth\n      height\n      id\n      imageSizes {\n        size_disp {\n          height\n          url\n          width\n        }\n        size_fs {\n          height\n          url\n          width\n        }\n        size_max_1200 {\n          height\n          url\n          width\n        }\n        size_1400_opt_1 {\n          height\n          url\n          width\n        }\n        size_2800_opt_1 {\n          height\n          url\n          width\n        }\n      }\n      position\n      width\n    }\n    id\n    fullBleed\n    sortType\n  }\n\n        \n  fragment projectCoverFields on ProjectCoverImageSizes {\n    size_original {\n      url\n    }\n    size_115 {\n      url\n    }\n    size_202 {\n      url\n    }\n    size_230 {\n      url\n    }\n    size_404 {\n      url\n    }\n    size_808 {\n      url\n    }\n    size_max_808 {\n      url\n    }\n  }\n\n        \n  fragment projectStylesFields on ProjectStyle {\n    background {\n      color\n    }\n    divider {\n      borderStyle\n      borderWidth\n      display\n      fontSize\n      height\n      lineHeight\n      margin\n      position\n      top\n    }\n    spacing {\n      moduleBottomMargin\n      projectTopMargin\n    }\n  }\n\n        \n  fragment projectTeamFields on TeamItem {\n    displayName\n    id\n    imageSizes {\n      size_115 {\n        height\n        url\n        width\n      }\n      size_138 {\n        height\n        url\n        width\n      }\n      size_276 {\n        height\n        url\n        width\n      }\n    }\n    locationDisplay\n    slug\n    url\n  }\n\n        \n  fragment projectToolFields on Tool {\n    approved\n    backgroundColor\n    backgroundImage {\n      size_original {\n        height\n        url\n        width\n      }\n      size_max_808 {\n        height\n        url\n        width\n      }\n      size_404 {\n        height\n        url\n        width\n      }\n    }\n    category\n    categoryLabel\n    categoryId\n    id\n    synonym {\n      authenticated\n      downloadUrl\n      galleryUrl\n      iconUrl\n      iconUrl2x\n      name\n      synonymId\n      tagId\n      title\n      type\n      url\n    }\n    title\n    url\n  }\n\n        \n  fragment projectTagFields on Tag {\n    category\n    id\n    title\n  }\n\n        \n  fragment sourceFileWithRenditionsFields on SourceFile {\n    __typename\n    sourceFileId\n    projectId\n    userId\n    title\n    assetId\n    renditionUrl\n    mimeType\n    size\n    category\n    licenseType\n    unitAmount\n    currency\n    tier\n    hidden\n    extension\n    hasUserPurchased\n    description\n    renditions {\n      etag\n      fileName\n      id\n      md5\n      mimeType\n      size\n      srcUrl\n    }\n    cover {\n      coverUrl\n      coverX\n      coverY\n      coverScale\n    }\n  }\n\n        \n  fragment sourceLinkFields on LinkedAsset {\n    __typename\n    name\n    premium\n    url\n    category\n    licenseType\n  }\n\n      ",
        #                                                                             "variables": {
        #                                                                                 "projectId": 243693391,
        #                                                                                 "params": {
        #                                                                                     "agencies": "",
        #                                                                                     "assets": [],
        #                                                                                     "backgroundColor": "FFFFFF",
        #                                                                                     "brands": "",
        #                                                                                     "captionStyles": {
        #                                                                                         "color": "a4a4a4",
        #                                                                                         "fontFamily": "helvetica,arial,sans-serif",
        #                                                                                         "fontSize": 14,
        #                                                                                         "fontStyle": "italic",
        #                                                                                         "fontWeight": "normal",
        #                                                                                         "lineHeight": 1.4,
        #                                                                                         "textAlign": "left",
        #                                                                                         "textDecoration": "none",
        #                                                                                         "textTransform": "none",
        #                                                                                     },
        #                                                                                     "canvasTopMargin": 80,
        #                                                                                     "commentsStatus": "ALLOWED",
        #                                                                                     "coowners": "2044610771",
        #                                                                                     "creativeFields": "",
        #                                                                                     "credits": "",
        #                                                                                     "description": "",
        #                                                                                     "license": "NO_USE",
        #                                                                                     "linkStyles": {
        #                                                                                         "color": "1769FF",
        #                                                                                         "fontFamily": "helvetica,arial,sans-serif",
        #                                                                                         "fontSize": 20,
        #                                                                                         "fontStyle": "normal",
        #                                                                                         "fontWeight": "normal",
        #                                                                                         "lineHeight": 1.4,
        #                                                                                         "textAlign": "left",
        #                                                                                         "textDecoration": "none",
        #                                                                                         "textTransform": "none",
        #                                                                                     },
        #                                                                                     "matureContentStatus": "OFF",
        #                                                                                     "modules": [
        #                                                                                         {
        #                                                                                             "imageModule": {
        #                                                                                                 "id": 1406309813,
        #                                                                                                 "alignment": "center",
        #                                                                                                 "captionAlignment": "left",
        #                                                                                                 "fullBleed": "NO",
        #                                                                                                 "caption": "",
        #                                                                                                 "tags": [],
        #                                                                                                 "altText": "Image may contain: screenshot",
        #                                                                                             }
        #                                                                                         },
        #                                                                                         {
        #                                                                                             "imageModule": {
        #                                                                                                 "id": 1406309815,
        #                                                                                                 "alignment": "center",
        #                                                                                                 "captionAlignment": "left",
        #                                                                                                 "fullBleed": "NO",
        #                                                                                                 "caption": "",
        #                                                                                                 "tags": [],
        #                                                                                                 "altText": "Image may contain: screenshot",
        #                                                                                             }
        #                                                                                         },
        #                                                                                         {
        #                                                                                             "imageModule": {
        #                                                                                                 "id": 1406309817,
        #                                                                                                 "alignment": "center",
        #                                                                                                 "captionAlignment": "left",
        #                                                                                                 "fullBleed": "NO",
        #                                                                                                 "caption": "",
        #                                                                                                 "tags": [],
        #                                                                                                 "altText": "Image may contain: screenshot",
        #                                                                                             }
        #                                                                                         },
        #                                                                                         {
        #                                                                                             "imageModule": {
        #                                                                                                 "id": -1,
        #                                                                                                 "alignment": "center",
        #                                                                                                 "captionAlignment": "left",
        #                                                                                                 "fullBleed": "NO",
        #                                                                                                 "srcUrl": "https://s3.amazonaws.com/be-network-tmp-prod-ue1-a/582302bc-ec29-4b76-9842-02193e6558ef.png",
        #                                                                                                 "caption": "",
        #                                                                                             }
        #                                                                                         },
        #                                                                                     ],
        #                                                                                     "moduleBottomMargin": 60,
        #                                                                                     "paragraphStyles": {
        #                                                                                         "color": "696969",
        #                                                                                         "fontFamily": "helvetica,arial,sans-serif",
        #                                                                                         "fontSize": 20,
        #                                                                                         "fontStyle": "normal",
        #                                                                                         "fontWeight": "normal",
        #                                                                                         "lineHeight": 1.4,
        #                                                                                         "textAlign": "left",
        #                                                                                         "textDecoration": "none",
        #                                                                                         "textTransform": "none",
        #                                                                                     },
        #                                                                                     "publishStatus": "DRAFT",
        #                                                                                     "schools": "",
        #                                                                                     "subTitleStyles": {
        #                                                                                         "color": "a4a4a4",
        #                                                                                         "fontFamily": "helvetica,arial,sans-serif",
        #                                                                                         "fontSize": 20,
        #                                                                                         "fontStyle": "normal",
        #                                                                                         "fontWeight": "normal",
        #                                                                                         "lineHeight": 1.4,
        #                                                                                         "textAlign": "left",
        #                                                                                         "textDecoration": "none",
        #                                                                                         "textTransform": "none",
        #                                                                                     },
        #                                                                                     "tags": "",
        #                                                                                     "teams": "",
        #                                                                                     "titleStyles": {
        #                                                                                         "color": "191919",
        #                                                                                         "fontFamily": "helvetica,arial,sans-serif",
        #                                                                                         "fontSize": 36,
        #                                                                                         "fontStyle": "normal",
        #                                                                                         "fontWeight": "bold",
        #                                                                                         "lineHeight": 1.1,
        #                                                                                         "textAlign": "left",
        #                                                                                         "textDecoration": "none",
        #                                                                                         "textTransform": "none",
        #                                                                                     },
        #                                                                                     "tools": "",
        #                                                                                     "visibleNetworkIds": "0",
        #                                                                                 },
        #                                                                             },
        #                                                                         }

        #                                                                         async with (
        #                                                                             session.post(
        #                                                                                 url,
        #                                                                                 headers={
        #                                                                                     **self.headers,
        #                                                                                     "authorization": f"Bearer {self.authorization_bearer}",
        #                                                                                     "content-type": "application/json",
        #                                                                                 },
        #                                                                                 json={
        #                                                                                     **payload,
        #                                                                                     "variables": {
        #                                                                                         **payload[
        #                                                                                             "variables"
        #                                                                                         ],
        #                                                                                         "params": {
        #                                                                                             **payload[
        #                                                                                                 "variables"
        #                                                                                             ][
        #                                                                                                 "params"
        #                                                                                             ],
        #                                                                                             "modules": all_modules_mapped,
        #                                                                                         },
        #                                                                                     },
        #                                                                                 },
        #                                                                             ) as response
        #                                                                         ):
        #                                                                             if (
        #                                                                                 response.status
        #                                                                                 == 200
        #                                                                             ):
        #                                                                                 json_data = await response.json()
        #                                                                                 if (
        #                                                                                     json_data
        #                                                                                     and "data"
        #                                                                                     in json_data
        #                                                                                     and "updateProject"
        #                                                                                     in json_data[
        #                                                                                         "data"
        #                                                                                     ]
        #                                                                                 ):
        #                                                                                     print(
        #                                                                                         f"{project_id} updated successfully"
        #                                                                                     )
        #                                                                                     return json_data[
        #                                                                                         "data"
        #                                                                                     ][
        #                                                                                         "updateProject"
        #                                                                                     ][
        #                                                                                         "allModules"
        #                                                                                     ]
        #                                                                             raise Exception(
        #                                                                                 "Failed to update project"
        #                                                                             )

    async def createProject(self, description=None):
        url = f"https://www.{ecnaheb_url_api}/v2/project/editor"
        payload = {
            "privacy": "public",
            "credits": "",
            "teams": "",
            "visible_to": "",
            "tools": "",
            "description": "description",
            "published": "0",
            "cover_source_url": "",
            "background_source_url": "",
            "allow_comments": "1",
            "fields": "",
            "tags": "",
            "mature_content": "0",
            "brands": "",
            "agencies": "",
            "schools": "",
            "coowners": "2044610771",
            "license": "no-use",
            "title_font_family": "helvetica,arial,sans-serif",
            "title_font_style": "normal",
            "title_font_weight": "bold",
            "title_text_align": "left",
            "title_text_decoration": "none",
            "title_text_transform": "none",
            "title_color": "191919",
            "title_font_size": "36",
            "title_line_height": "1.1",
            "subtitle_font_family": "helvetica,arial,sans-serif",
            "subtitle_font_style": "normal",
            "subtitle_font_weight": "normal",
            "subtitle_text_align": "left",
            "subtitle_text_decoration": "none",
            "subtitle_text_transform": "none",
            "subtitle_color": "a4a4a4",
            "subtitle_font_size": "20",
            "subtitle_line_height": "1.4",
            "paragraph_font_family": "helvetica,arial,sans-serif",
            "paragraph_font_style": "normal",
            "paragraph_font_weight": "normal",
            "paragraph_text_align": "left",
            "paragraph_text_decoration": "none",
            "paragraph_text_transform": "none",
            "paragraph_color": "696969",
            "paragraph_font_size": "20",
            "paragraph_line_height": "1.4",
            "caption_font_family": "helvetica,arial,sans-serif",
            "caption_font_style": "italic",
            "caption_font_weight": "normal",
            "caption_text_align": "left",
            "caption_text_decoration": "none",
            "caption_text_transform": "none",
            "caption_color": "a4a4a4",
            "caption_font_size": "14",
            "caption_line_height": "1.4",
            "link_font_family": "helvetica,arial,sans-serif",
            "link_font_style": "normal",
            "link_font_weight": "normal",
            "link_text_align": "left",
            "link_text_decoration": "none",
            "link_text_transform": "none",
            "link_color": "1769FF",
            "link_font_size": "20",
            "link_line_height": "1.4",
            "background_color": "FFFFFF",
            "canvas_top_margin": "80",
            "module_bottom_margin": "60",
            "divider_type": "",
            "modules": "",
            "visible_network_ids": "",
            "assets": "",
            "format": "display",
        }
        # response = requests.post(
        #     url,
        #     headers={
        #         **self.headers,
        #         "authorization": f"Bearer {self.authorization_bearer}",
        #         "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        #     },
        # )
        # print(url)
        # if response.status_code == 201:
        #     json_data = response.json()
        #     if "project" in json_data:
        #         print("New project created")
        #         return json_data["project"]
        # else:
        #     raise Exception(f"Unexpected status code: {response.status_code}")
        # wh
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    **self.headers,
                    "authorization": f"Bearer {self.authorization_bearer}",
                    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                },
                data=payload,
            )
            if response.status_code == 201:
                json_data = response.json()
                if "project" in json_data:
                    print("New project created")
                    return json_data["project"]
            else:
                raise Exception(f"Unexpected status code: {response.status_code}")
        # req = requests.get("https://www.google.com")
        # print(req)
        # timeout = aiohttp.ClientTimeout(total=None, connect=None, sock_connect=None)
        # async with aiohttp.ClientSession(timeout=timeout) as session:
        #     async with session.post(
        #         url,
        #         headers={
        #             **self.headers,
        #             "authorization": f"Bearer {self.authorization_bearer}",
        #             "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        #         },
        #         data=payload,
        #         ssl=False,
        #     ) as response:
        #         if response.status == 201:
        #             json_data = await response.json()
        #             if "project" in json_data:
        #                 print("New project created")
        #                 return json_data["project"]
        #         else:
        #             raise Exception(f"Unexpected status code: {response.status}")
