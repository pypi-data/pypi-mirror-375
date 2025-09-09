# SPDX-FileCopyrightText: 2023 Helge
# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from fediverse_pasture_inputs.format import as_details
from fediverse_pasture_inputs.types import InputData, Support, Details
from fediverse_pasture_inputs.utils import format_as_json

mention_examples = [
    {
        "content": "basic mention; mention as list of dictionaries",
        "tag": [
            {
                "type": "Mention",
                "name": "@actor@test_server",
                "href": "http://pasture-one-actor/actor",
            }
        ],
    },
    {
        "content": "text @actor@pasture-one-actor; mention as dictionary",
        "tag": {
            "type": "Mention",
            "name": "@actor@test_server",
            "href": "http://pasture-one-actor/actor",
        },
    },
    {
        "content": "unrelated text",
        "tag": {
            "type": "Mention",
            "name": "something something",
            "href": "http://pasture-one-actor/actor",
        },
    },
    {
        "content": "Missing Name @actor@pasture-one-actor",
        "tag": {
            "type": "Mention",
            "href": "http://pasture-one-actor/actor",
        },
    },
    {
        "content": "realworld url",
        "tag": {
            "type": "Mention",
            "name": "@the_milkman@mastodon.social",
            "href": "https://mastodon.social/users/the_milkman",
        },
    },
    {
        "content": "unresolvable url -- https",
        "tag": {
            "type": "Mention",
            "name": "@dummy@example",
            "href": "https://dummy.example",
        },
    },
    {
        "content": "texunresolvable url -- http",
        "tag": {
            "type": "Mention",
            "name": "@test_actor@test_server",
            "href": "http://test_actor",
        },
    },
    {
        "content": "name is 'yay'",
        "tag": {
            "type": "as:Mention",
            "name": "yay",
            "href": "http://pasture-one-actor/actor",
        },
    },
    {
        "content": "@actor text",
        "tag": {
            "name": "@actor",
            "href": "http://pasture-one-actor/actor",
        },
    },
    {
        "content": "duplicate mention, see https://codeberg.org/funfedidev/fediverse-pasture-inputs/issues/75",
        "tag": [
            {
                "type": "Mention",
                "name": "@actor@test_server",
                "href": "http://pasture-one-actor/actor",
            },
            {
                "type": "Mention",
                "name": "@actor@test_server",
                "href": "http://pasture-one-actor/actor",
            },
        ],
    },
]


def mastodon_support(data):
    if not data:
        return "❌"
    if len(data.get("mentions", [])) > 0:
        return "✅ mention"
    return "parsed"


def activity_support(x):
    obj = x.get("object", {})
    return as_details(obj.get("content"), format_as_json(obj.get("tag"))[0])


support = Support(
    title="tag",
    result={
        "activity": activity_support,
        "mastodon": mastodon_support,
        "misskey": mastodon_support,
    },
)

details = Details(
    extractor={
        "activity": lambda x: format_as_json(x.get("object", {}).get("tag")),
        "mastodon": lambda x: format_as_json(x.get("mentions")),
        "misskey": lambda x: format_as_json(x.get("mentions")),
    },
    title={
        "mastodon": "| tag | mentions | Example |",
        "misskey": "| tag | mentions | Example |",
    },
)

data = InputData(
    title="Mentions",
    frontmatter="""Mentions are discussed in [this section of
ActivityStreams](https://www.w3.org/TR/activitystreams-vocabulary/#microsyntaxes).

The big difference on if mentions are parsed are currently
a result of if the value in `href` can be resolved by the
application being tested.

In the support table `parsed` means that the activity could be parsed, but the mention was discarded.
A ❌ in the support table means that the entire message has failed to parse.
""",
    filename="mentions.md",
    group="Object Content",
    examples=mention_examples,
    details=details,
    support=support,
)
