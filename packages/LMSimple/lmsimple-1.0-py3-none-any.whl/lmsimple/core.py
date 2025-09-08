"""."""

# ruff: noqa: D103 SLF001 S323

from __future__ import annotations

import asyncio
import base64
import contextlib
import json
import logging
import re
import ssl
from pathlib import Path

import aiohttp
import websockets
from selectolax.parser import HTMLParser

from lmsimple.backend import find_process_fullname
from lmsimple.constants import ROLES, SPELLS
from lmsimple.models import (
    Block,
    Item,
    ItemSet,
    Payload_ItemSets,
    Payload_Perks,
    Payload_Spells,
)

logging.basicConfig(level=10)

_last_champion_id = None


def lcu_lockfile(league_exe: str) -> Path:
    if not Path(league_exe).exists():
        msg = "LeagueClient.exe not running or not found."
        raise ProcessLookupError(msg)
    league_dir = Path(league_exe).parent
    return Path(league_dir / "lockfile")


def lcu_wss(lockfile: Path) -> dict[str, str]:
    with lockfile.open() as f:
        content = f.read()
    parts = content.split(":")

    port = parts[2]
    wss = f"wss://127.0.0.1:{port}"
    https = f"https://127.0.0.1:{port}"

    auth_key = parts[3]
    raw_auth = f"riot:{auth_key}"
    auth = base64.b64encode(bytes(raw_auth, "utf-8")).decode()
    return {"auth": auth, "wss": wss, "https": https}


async def get_champion_name(
    client: aiohttp.ClientSession,
    champion_id: int,
) -> str | None:
    response = await client.get("https://ddragon.leagueoflegends.com/api/versions.json")
    content = await response.json()
    latest_ddragon_ver = content[0]

    response = await client.get(
        f"https://ddragon.leagueoflegends.com/cdn/{latest_ddragon_ver}/data/en_US/champion.json",
    )
    content = await response.json()
    ddragon_data = content["data"]
    name = ""
    for item in ddragon_data.values():
        if item["key"] == str(champion_id):
            name = item["id"]
    if name:
        return name
    return None


async def on_message(event: str | bytes, https: str, headers: dict) -> None:  # noqa: C901 PLR0915 PLR0912
    try:
        _data = json.loads(event)[2]
        data = _data["data"]
        local_p_cell_id = data["localPlayerCellId"]
        my_team = data["myTeam"]
        champion_id = 0
        summoner_id = 0
        assigned_position = None
        for p in my_team:
            if p["cellId"] == local_p_cell_id:
                if str(p["championId"]).strip() != "0":
                    champion_id = p["championId"]
                else:
                    champion_id = p["championPickIntent"]
                assigned_position = p["assignedPosition"]
                summoner_id = p["summonerId"]
        async with aiohttp.ClientSession(base_url=https, headers=headers) as conn:
            champion_name = (
                await get_champion_name(conn, champion_id) if champion_id else None
            )
            role = ROLES.get(assigned_position, None) if assigned_position else None
            build_page_url = (
                f"https://mobalytics.gg/lol/champions/{champion_name}/build/{role}"
                if role is not None
                else f"https://mobalytics.gg/lol/champions/{champion_name}/aram-builds"
            )
            response = await conn.get(build_page_url)
            content = await response.text()
            tree = HTMLParser(content)
            # &Itemsets ----------------------------------------------------------------
            nodes = tree.css(Payload_ItemSets.itemsets_css)
            blocks: list[Block] = []
            for node in nodes:
                block_name_node = node.css_first("h4")
                block_name = block_name_node.text() if block_name_node else ""
                items_node = node.css(".m-5o4ika")
                block_items: list[Item] = []
                for item_node in items_node:
                    item = item_node.attributes.get("src")
                    matches = re.search("(\\d+)\\.png", item) if item else None
                    if matches is not None:
                        block_items.append(Item(1, matches.group(1)))
                block = Block(block_items, block_name)
                blocks.append(block)
            itemsets = ItemSet(
                [champion_id],
                blocks,
                f"{champion_name} ({role})" if role else f"{champion_name} (ARAM)",
            )
            itemsets_payload = Payload_ItemSets(
                accountId=summoner_id,
                itemSets=[itemsets],
                timestamp=0,
            )

            # &Perks -------------------------------------------------------------------
            nodes = tree.css(Payload_Perks.main_perks_css)
            main_perks = []
            selected_perks = []
            for node in nodes:
                src = node.attributes.get("src")
                matches = re.search("/(\\d+)\\.svg", src) if src else None
                if matches:
                    main_perks.append(int(matches.group(1)))
            for css in Payload_Perks.selected_perks_css:
                nodes = tree.css(css)
                for node in nodes:
                    src = node.attributes.get("src")
                    matches = (
                        re.search("/(\\d+)(\\.svg|\\.png)\\b", src) if src else None
                    )
                    if matches:
                        selected_perks.append(int(matches.group(1)))
            perks_payload = Payload_Perks(
                name=f"{champion_name} - {role}" if role else f"{champion_name} - ARAM",
                current=True,
                primaryStyleId=int(main_perks[0]),
                subStyleId=int(main_perks[1]),
                selectedPerkIds=selected_perks,
            )
            # &Spells ------------------------------------------------------------------
            nodes = tree.css(Payload_Spells.spells_css)
            spells_ids = []
            for node in nodes:
                src = node.attributes.get("src")
                matches = re.search("(\\w+)\\.png", src) if src else None
                if matches:
                    spells_ids.append(SPELLS[matches[1]])
            spells_payload = Payload_Spells(
                selectedSkinId=champion_id,
                spell1Id=int(spells_ids[0]),
                spell2Id=int(spells_ids[1]),
            )
            global _last_champion_id  # noqa: PLW0603
            if _last_champion_id != champion_id:
                await asyncio.gather(
                    send_itemsets(conn, itemsets_payload),
                    send_perks(conn, perks_payload),
                    send_spells(conn, spells_payload),
                )
            _last_champion_id = champion_id
            await conn.close()
    except (json.decoder.JSONDecodeError, KeyError, TypeError, IndexError):
        pass
    except KeyboardInterrupt:
        raise


async def send_itemsets(
    client: aiohttp.ClientSession,
    payload: Payload_ItemSets,
) -> None:
    await client.put(
        url=payload.endpoint_put,
        json=payload.asdict(),
        ssl=ssl._create_unverified_context(),
    )


async def send_perks(client: aiohttp.ClientSession, payload: Payload_Perks) -> None:
    with contextlib.suppress(KeyError):
        response = await client.get(
            url=payload.endpoint_get,
            ssl=ssl._create_unverified_context(),
        )
        content = await response.json()
        page_id = content["id"]
        if page_id:
            payload.endpoint_delete = page_id
            await client.delete(
                url=payload.endpoint_delete,
                ssl=ssl._create_unverified_context(),
            )

    await client.post(
        url=payload.endpoint_post,
        json=payload.asdict(),
        ssl=ssl._create_unverified_context(),
    )


async def send_spells(client: aiohttp.ClientSession, payload: Payload_Spells) -> None:
    await client.patch(
        url=payload.endpoint_patch,
        json=payload.asdict(),
        ssl=ssl._create_unverified_context(),
    )


async def start() -> int:
    exe = find_process_fullname("LeagueClient.exe")
    if not exe:
        msg = "league.exe not found."
        raise RuntimeError(msg)
    lockfile = lcu_lockfile(exe)
    lockfile_data = lcu_wss(lockfile)
    https = lockfile_data["https"]
    wss = lockfile_data["wss"]
    auth = lockfile_data["auth"]
    header = {"Authorization": f"Basic {auth}"}

    try:
        async with websockets.connect(
            uri=wss,
            additional_headers=header,
            ssl=ssl._create_unverified_context(),
        ) as ws:
            await ws.send('[2,"0", "GetLolSummonerV1CurrentSummoner"]')
            json.loads(await ws.recv())
            await ws.send('[5, "OnJsonApiEvent_lol-champ-select_v1_session"]')
            async for event in ws:
                await on_message(event, https, header)
    except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
        pass
    return 0
