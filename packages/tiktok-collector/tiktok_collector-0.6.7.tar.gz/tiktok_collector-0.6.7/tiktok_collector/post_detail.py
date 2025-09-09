import requests


class TiktokPostDetailCollector:
    """
    A class to collect TikTok posts by keyword.
    """

    # Constants
    NO_WATERMARK_API_URL = (
        "https://tiktok-video-no-watermark2.p.rapidapi.com/comment/list"
    )
    NO_WATERMARK_RAPID_API_HOST = "tiktok-video-no-watermark2.p.rapidapi.com"

    API_URL = "https://api.tokapi.online/v1/post/{post_id}"
    RAPID_API_HOST = "tokapi"

    def __init__(self, api_key):
        """
        Initialize the collector with an API key and configuration.

        Args:
            api_key (str): Your RapidAPI key for TikTok API
            country_code (str): The country code to filter posts by (default: "US")
            max_post_by_keyword (int): Maximum number of posts to collect per keyword (default: 100)
            max_keyword_post_retry (int): Maximum number of retries for keyword post collection (default: 3)
        """
        self.api_key = api_key
        self.no_watermark_headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.NO_WATERMARK_RAPID_API_HOST,
        }

        self.headers = {
            "accept": "application/json",
            "x-api-key": self.api_key,
            "x-project-name": self.RAPID_API_HOST,
        }

    def collect_comments_by_post(self, post_id, country_code="GB"):

        try:
            comment_list = self._search_comments(post_id, country_code)
            print(f"Found {len(comment_list)} comments for post {post_id}")

            comment_full = []
            for cmt in comment_list:
                try:
                    info = {
                        "post_id": post_id,
                        "comment_id": cmt.get("cid"),
                        "text": cmt.get("text"),
                        "create_time": cmt.get("create_time"),
                        "num_like": cmt.get("digg_count"),
                        "num_reply": cmt.get("reply_comment_total") or 0,
                        "user_id": cmt.get("user", {}).get("uid"),
                        "user_name": cmt.get("user", {}).get("unique_id"),
                        "full_name": cmt.get("user", {}).get("nickname", None),
                        "avatar_url": cmt.get("user", {}).get("avatar", None),
                        "bio": cmt.get("user", {}).get("signature", None),
                        "bio_url": cmt.get("user", {}).get("bio_url", None),
                        "num_follower": cmt.get("user", {}).get("follower_count", None),
                        "num_following": cmt.get("user", {}).get(
                            "following_count", None
                        ),
                        "num_post": cmt.get("user", {}).get("aweme_count", None),
                        "youtube_channel_id": cmt.get("user", {}).get(
                            "youtube_channel_id", None
                        ),
                        "ins_id": cmt.get("user", {}).get("ins_id", None),
                        "live_commerce": cmt.get("user", {}).get("live_commerce", None),
                        "region": cmt.get("user", {}).get("region", None),
                    }
                except Exception as error:
                    print(f"Error processing post: {error}")
                    continue
                comment_full.append(info)

            return comment_full

        except Exception as e:
            print(f"Error collecting posts for keyword {post_id}: {e}")
            return []

    def _get_detail(self, post_id, country_code="GB"):
        post_info = None
        retry = 0
        while True:
            try:
                querystring = {"region": country_code}
                response = requests.get(
                    self.API_URL.format(post_id=post_id),
                    headers=self.headers,
                    params=querystring,
                )

                data = response.json()

                collected_post = data.get("aweme_detail")
                if collected_post:
                    post_info = TiktokPostDetailCollector.clean_post(collected_post)
                    break
            except Exception as e:
                print("Load post detail error", e)
                retry += 1
            retry += 1
            if retry > 3:
                break

        return post_info

    @staticmethod
    def clean_post(item):
        return {
            "_id": item.get("aweme_id"),
            "post_id": item.get("aweme_id"),
            "content_id": item.get("aweme_id"),
            "num_comment": item.get("statistics", {}).get("comment_count"),
            "num_like": item.get("statistics", {}).get("digg_count"),
            "num_reaction": item.get("statistics", {}).get("digg_count"),
            "num_view": item.get("statistics", {}).get("play_count"),
            "num_share": item.get("statistics", {}).get("share_count"),
            "num_save": item.get("statistics", {}).get("collect_count"),
            "username": item.get("author", {}).get("unique_id"),
            "user_id": item.get("author", {}).get("uid"),
            "num_follower": item.get("author", {}).get("follower_count"),
            "social_username": item.get("author", {}).get("unique_id"),
            "social_id": item.get("author", {}).get("uid"),
            "caption": item.get("desc"),
            "taken_at_timestamp": item.get("create_time"),
            "display_url": item.get("video", {})
            .get("origin_cover", {})
            .get("url_list"),
            "region": item.get("region"),
            "ecommerce_product_info": item.get("anchors_extras"),
            "anchors": item.get("anchors"),
            "transcript_url": (
                item.get("video", {})
                .get("cla_info", {})
                .get("caption_infos", {})[0]
                .get("url")
                if isinstance(
                    item.get("video", {}).get("cla_info", {}).get("caption_infos", {}),
                    list,
                )
                else None
            ),
        }
