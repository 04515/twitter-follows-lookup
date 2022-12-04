import requests
import os
import csv
import re


##### FUNCTIONS
# usernames：ユーザー名　user_fields:取得データ　APIリクエスト用のURLを作成
def create_url(user_id, ff, max_results, next_token, user_fields):
    if (any(user_fields)):
        formatted_user_fields = "user.fields=" + ",".join(user_fields)
    else:
        formatted_user_fields = ""
    if (next_token is not None):
        formatted_next_token = "&pagination_token=" + (next_token)
    else:
        formatted_next_token = ""
    if (max_results > 1000): max_results = 1000
    # &pagination_token=
    url = "https://api.twitter.com/2/users/{}/{}?max_results={}{}&{}".format(user_id, ff, max_results,
                                                                             formatted_next_token,
                                                                             formatted_user_fields)
    return url


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))
    return response.json()


# filename：出力ファイル名 header:ヘッダー contents_list:中身
def save_csvfile(filename, header, contents_list):
    if (not os.path.isfile(filename)):  # 既存の同名ファイルがなければ新規作成
        with open(filename, "w", newline="", encoding="utf-16") as f:
            w = csv.DictWriter(f, fieldnames=header, dialect="excel-tab", quoting=csv.QUOTE_ALL)
            w.writeheader()

    with open(filename, "a", newline="", encoding="utf-16") as f:
        w = csv.DictWriter(f, fieldnames=header, dialect="excel-tab", quoting=csv.QUOTE_ALL)
        for contents in contents_list:
            for k in contents.keys():  #### 文字列内のNullを除去
                if (type(contents[k]) is str): contents[k] = contents[k].replace("\0", "")
            w.writerow(contents)


#### MAIN
def main():
    #### VARIABLES
    # APIキー https://developer.twitter.com から取得
    BEARER_TOKEN = r"AAAAAAAAAAAAAAAAAAAAAMAukAEAAAAAV1HKiYyDoz%2BCkWjdQXVYGNl1A%2B8%3DWFOml3c4itWz8reVdHAmF9dPufaN7KVUV4DMuSsl0BHcXSGYgZ"
    # ユーザーID
    user_id = 1249198073990885376
    # フォローしてる人を探すときは[0] フォロワーを探すときは[1]
    ff = ["following", "followers"][0]
    # 取得したいデータ数
    max_results = 1700

    # 取得データ  e.g. user_fields = ["id", "name", "username", "created_at", "description"]
    # created_at(作成時刻), description(アカウントの自己紹介)などの情報が欲しい場合はtweet_fieldsに書く
    user_fields = ["id", "name", "username", "created_at", "protected",
                   "withheld", "location", "url", "description", "verified", "entities",
                   "profile_image_url", "public_metrics", "pinned_tweet_id"]

    #### データ取得
    next_token = None
    data_len = 0
    while (True):
        url = create_url(user_id, ff, max_results, next_token, user_fields)
        headers = create_headers(BEARER_TOKEN)
        json_response = connect_to_endpoint(url, headers)
        data = json_response["data"]
        meta = json_response["meta"]

        #### 取得データ保存(user_id + [following or followers] + .csv)
        csv_file_name = re.sub(r'[\\/:*?"<>|.]+', '', str(user_id) + "_" + ff) + ".csv"  # ファイルに使えない文字削除
        save_csvfile(csv_file_name, user_fields, data)

        #### 終了チェック(欲しい数に達するか全て取り終わったら終了)
        data_len += len(data)
        if (max_results <= data_len): break
        if (not "next_token" in meta): break
        next_token = meta["next_token"]
    pass


if __name__ == "__main__":
    main()
