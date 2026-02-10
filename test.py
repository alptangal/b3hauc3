import httpx
import requests

req = httpx.get(
    "https://www.behance.net/",
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Trailer/93.3.3570.29",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://www.behance.net/alphatango2",
        "Cookie": 'gk_suid=98470405; gki=; bcp=ce90ca5b-0ebd-4b49-92ca-3255c05770b0; bcp_generated=1770696500935; g_state={"i_l":0,"i_ll":1770696566276,"i_b":"xZ2HCDXoPu2BGAfjksuuNYvf1/ltef5hzV764R1QPL0","i_e":{"enable_itp_optimization":15}}; OptanonAlertBoxClosed=2026-02-10T04:08:26.910Z; OptanonConsent=groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1; bcp_susi_initiated_at=1770696510263; iat0=eyJhbGciOiJSUzI1NiIsIng1dSI6Imltc19uYTEta2V5LWF0LTEuY2VyIiwia2lkIjoiaW1zX25hMS1rZXktYXQtMSIsIml0dCI6ImF0In0.eyJpZCI6IjE3NzA2OTY1NjUxNThfZjA1ZmIwYjQtYTFhNS00OGJlLWFjYTMtMDY5N2MyM2E3MGQ1X3V3MiIsInR5cGUiOiJhY2Nlc3NfdG9rZW4iLCJjbGllbnRfaWQiOiJCZWhhbmNlV2ViU3VzaTEiLCJ1c2VyX2lkIjoiRDFENjIxQ0Q2ODlCNzVBNjBBNDk1Q0U4QEFkb2JlSUQiLCJzdGF0ZSI6IntcImFjXCI6XCJiZWhhbmNlLm5ldFwiLFwiY3NyZlwiOlwiY2U5MGNhNWItMGViZC00YjQ5LTkyY2EtMzI1NWMwNTc3MGIwXCIsXCJ0aW1lc3RhbXBcIjpcIjE3NzA2OTY1MDA5MzVcIixcImNvbnRleHRcIjp7XCJpbnRlbnRcIjpcInNpZ25JblwifSxcImpzbGlidmVyXCI6XCJ2Mi12MC40OS4wLTEyLWdmYjE3OTJhXCIsXCJub25jZVwiOlwiMzg2Njc3ODM1NDM3OTMxNlwifSIsImFzIjoiaW1zLW5hMSIsImFhX2lkIjoiRDFENjIxQ0Q2ODlCNzVBNjBBNDk1Q0U4QEFkb2JlSUQiLCJjdHAiOjAsImZnIjoiMkdISlNVNjdWTE01QURVS0ZBUVZJSEFBRTQ9PT09PT0iLCJzaWQiOiIxNzcwNjk2NTY1MTUzX2JkNTllYjIzLWU3ZWEtNDYyMi1hZjM3LTY0YzU4Mzc3NzY5N191dzIiLCJtb2kiOiIxMDUxMGFkYyIsInBiYSI6Ik1lZFNlY05vRVYsTG93U2VjIiwiZXhwaXJlc19pbiI6Ijg2NDAwMDAwIiwic2NvcGUiOiJBZG9iZUlELG9wZW5pZCxnbmF2LHNhby5jY2VfcHJpdmF0ZSxjcmVhdGl2ZV9jbG91ZCxjcmVhdGl2ZV9zZGssYmUucHJvMi5leHRlcm5hbF9jbGllbnQsYWRkaXRpb25hbF9pbmZvLnJvbGVzLGltc19jYWkudmVyaWZpZWRJZC5yZWFkLGltc19jYWkuc29jaWFsLnJlYWQsaW1zX2NhaS5zb2NpYWwud29ya3BsYWNlLnJlYWQiLCJjcmVhdGVkX2F0IjoiMTc3MDY5NjU2NTE1OCJ9.B4-GdqP4RvGhSCRklCrTq5ciJLaQoB3SI3urSpC3557GL_qGP1PpxrpHNjRpqiJBycU2jxNhgbmQ78oCh9AKm5KaqxyHv6ewyeiaVcWoKwFXaCyM4l0SeYTiK-Lzsryop3LUyqf6l5ADHiVViNz2_4J7VHNQed63xQkX8pX5ynR97Xv4aNUpWWNZkJd2YYkrZ_Vwkx8GcSfy9dwDiVS66ZcA2m3cJ977GZr1ZeBv7TPOXDhDxeiIOjxtIE9AiD1gF9w7AIAbK3ZxREWK2kCBEnFRHyvbPdLDSj25ZrF_lsfbTfWoWmG204b4eBKQCnm8_aSSHd9YdE9vaquqKtf4gg; bein=1; dialog_dismissals=announcement_307%3Bnew_embed_type; did_user_close_profile_checklist=false',
    },
)

print(req)
