from pydantic import BaseModel, Field

import httpx
from typing import Any

from mcp.server.fastmcp import FastMCP

USER_AGENT = "cmp-tenki-app/1.0"
# Initialize FastMCP server
mcp = FastMCP("weather")
location_data = [
    {"pref": "Hokkaido", "city": "稚内", "id": "011000"},
    {"pref": "Hokkaido", "city": "旭川", "id": "012010"},
    {"pref": "Hokkaido", "city": "留萌", "id": "012020"},
    {"pref": "Hokkaido", "city": "網走", "id": "013010"},
    {"pref": "Hokkaido", "city": "北見", "id": "013020"},
    {"pref": "Hokkaido", "city": "紋別", "id": "013030"},
    {"pref": "Hokkaido", "city": "根室", "id": "014010"},
    {"pref": "Hokkaido", "city": "釧路", "id": "014020"},
    {"pref": "Hokkaido", "city": "帯広", "id": "014030"},
    {"pref": "Hokkaido", "city": "室蘭", "id": "015010"},
    {"pref": "Hokkaido", "city": "浦河", "id": "015020"},
    {"pref": "Hokkaido", "city": "札幌", "id": "016010"},
    {"pref": "Hokkaido", "city": "岩見沢", "id": "016020"},
    {"pref": "Hokkaido", "city": "倶知安", "id": "016030"},
    {"pref": "Hokkaido", "city": "函館", "id": "017010"},
    {"pref": "Hokkaido", "city": "江差", "id": "017020"},
    {"pref": "Aomori", "city": "青森", "id": "020010"},
    {"pref": "Aomori", "city": "むつ", "id": "020020"},
    {"pref": "Aomori", "city": "八戸", "id": "020030"},
    {"pref": "Iwate", "city": "盛岡", "id": "030010"},
    {"pref": "Iwate", "city": "宮古", "id": "030020"},
    {"pref": "Iwate", "city": "大船渡", "id": "030030"},
    {"pref": "Miyagi", "city": "仙台", "id": "040010"},
    {"pref": "Miyagi", "city": "白石", "id": "040020"},
    {"pref": "Akita", "city": "秋田", "id": "050010"},
    {"pref": "Akita", "city": "横手", "id": "050020"},
    {"pref": "Yamagata", "city": "山形", "id": "060010"},
    {"pref": "Yamagata", "city": "米沢", "id": "060020"},
    {"pref": "Yamagata", "city": "酒田", "id": "060030"},
    {"pref": "Yamagata", "city": "新庄", "id": "060040"},
    {"pref": "Fukushima", "city": "福島", "id": "070010"},
    {"pref": "Fukushima", "city": "小名浜", "id": "070020"},
    {"pref": "Fukushima", "city": "若松", "id": "070030"},
    {"pref": "Ibaraki", "city": "水戸", "id": "080010"},
    {"pref": "Ibaraki", "city": "土浦", "id": "080020"},
    {"pref": "Tochigi", "city": "宇都宮", "id": "090010"},
    {"pref": "Tochigi", "city": "大田原", "id": "090020"},
    {"pref": "Gunma", "city": "前橋", "id": "100010"},
    {"pref": "Gunma", "city": "みなかみ", "id": "100020"},
    {"pref": "Saitama", "city": "さいたま", "id": "110010"},
    {"pref": "Saitama", "city": "熊谷", "id": "110020"},
    {"pref": "Saitama", "city": "秩父", "id": "110030"},
    {"pref": "Chiba", "city": "千葉", "id": "120010"},
    {"pref": "Chiba", "city": "銚子", "id": "120020"},
    {"pref": "Chiba", "city": "館山", "id": "120030"},
    {"pref": "Tokyo", "city": "東京", "id": "130010"},
    {"pref": "Tokyo", "city": "大島", "id": "130020"},
    {"pref": "Tokyo", "city": "八丈島", "id": "130030"},
    {"pref": "Tokyo", "city": "父島", "id": "130040"},
    {"pref": "Kanagawa", "city": "横浜", "id": "140010"},
    {"pref": "Kanagawa", "city": "小田原", "id": "140020"},
    {"pref": "Niigata", "city": "新潟", "id": "150010"},
    {"pref": "Niigata", "city": "長岡", "id": "150020"},
    {"pref": "Niigata", "city": "高田", "id": "150030"},
    {"pref": "Niigata", "city": "相川", "id": "150040"},
    {"pref": "Toyama", "city": "富山", "id": "160010"},
    {"pref": "Toyama", "city": "伏木", "id": "160020"},
    {"pref": "Ishikawa", "city": "金沢", "id": "170010"},
    {"pref": "Ishikawa", "city": "輪島", "id": "170020"},
    {"pref": "Fukui", "city": "福井", "id": "180010"},
    {"pref": "Fukui", "city": "敦賀", "id": "180020"},
    {"pref": "Yamanashi", "city": "甲府", "id": "190010"},
    {"pref": "Yamanashi", "city": "河口湖", "id": "190020"},
    {"pref": "Nagano", "city": "長野", "id": "200010"},
    {"pref": "Nagano", "city": "松本", "id": "200020"},
    {"pref": "Nagano", "city": "飯田", "id": "200030"},
    {"pref": "Gifu", "city": "岐阜", "id": "210010"},
    {"pref": "Gifu", "city": "高山", "id": "210020"},
    {"pref": "Shizuoka", "city": "静岡", "id": "220010"},
    {"pref": "Shizuoka", "city": "網代", "id": "220020"},
    {"pref": "Shizuoka", "city": "三島", "id": "220030"},
    {"pref": "Shizuoka", "city": "浜松", "id": "220040"},
    {"pref": "Aichi", "city": "名古屋", "id": "230010"},
    {"pref": "Aichi", "city": "豊橋", "id": "230020"},
    {"pref": "Mie", "city": "津", "id": "240010"},
    {"pref": "Mie", "city": "尾鷲", "id": "240020"},
    {"pref": "Shiga", "city": "大津", "id": "250010"},
    {"pref": "Shiga", "city": "彦根", "id": "250020"},
    {"pref": "Kyoto", "city": "京都", "id": "260010"},
    {"pref": "Kyoto", "city": "舞鶴", "id": "260020"},
    {"pref": "Osaka", "city": "大阪", "id": "270000"},
    {"pref": "Hyogo", "city": "神戸", "id": "280010"},
    {"pref": "Hyogo", "city": "豊岡", "id": "280020"},
    {"pref": "Nara", "city": "奈良", "id": "290010"},
    {"pref": "Nara", "city": "風屋", "id": "290020"},
    {"pref": "Wakayama", "city": "和歌山", "id": "300010"},
    {"pref": "Wakayama", "city": "潮岬", "id": "300020"},
    {"pref": "Tottori", "city": "鳥取", "id": "310010"},
    {"pref": "Tottori", "city": "米子", "id": "310020"},
    {"pref": "Shimane", "city": "松江", "id": "320010"},
    {"pref": "Shimane", "city": "浜田", "id": "320020"},
    {"pref": "Shimane", "city": "西郷", "id": "320030"},
    {"pref": "Okayama", "city": "岡山", "id": "330010"},
    {"pref": "Okayama", "city": "津山", "id": "330020"},
    {"pref": "Hiroshima", "city": "広島", "id": "340010"},
    {"pref": "Hiroshima", "city": "庄原", "id": "340020"},
    {"pref": "Yamaguchi", "city": "下関", "id": "350010"},
    {"pref": "Yamaguchi", "city": "山口", "id": "350020"},
    {"pref": "Yamaguchi", "city": "柳井", "id": "350030"},
    {"pref": "Yamaguchi", "city": "萩", "id": "350040"},
    {"pref": "Tokushima", "city": "徳島", "id": "360010"},
    {"pref": "Tokushima", "city": "日和佐", "id": "360020"},
    {"pref": "Kagawa", "city": "高松", "id": "370000"},
    {"pref": "Ehime", "city": "松山", "id": "380010"},
    {"pref": "Ehime", "city": "新居浜", "id": "380020"},
    {"pref": "Ehime", "city": "宇和島", "id": "380030"},
    {"pref": "Kochi", "city": "高知", "id": "390010"},
    {"pref": "Kochi", "city": "室戸岬", "id": "390020"},
    {"pref": "Kochi", "city": "清水", "id": "390030"},
    {"pref": "Fukuoka", "city": "福岡", "id": "400010"},
    {"pref": "Fukuoka", "city": "八幡", "id": "400020"},
    {"pref": "Fukuoka", "city": "飯塚", "id": "400030"},
    {"pref": "Fukuoka", "city": "久留米", "id": "400040"},
    {"pref": "Saga", "city": "佐賀", "id": "410010"},
    {"pref": "Saga", "city": "伊万里", "id": "410020"},
    {"pref": "Nagasaki", "city": "長崎", "id": "420010"},
    {"pref": "Nagasaki", "city": "佐世保", "id": "420020"},
    {"pref": "Nagasaki", "city": "厳原", "id": "420030"},
    {"pref": "Nagasaki", "city": "福江", "id": "420040"},
    {"pref": "Kumamoto", "city": "熊本", "id": "430010"},
    {"pref": "Kumamoto", "city": "阿蘇乙姫", "id": "430020"},
    {"pref": "Kumamoto", "city": "牛深", "id": "430030"},
    {"pref": "Kumamoto", "city": "人吉", "id": "430040"},
    {"pref": "Oita", "city": "大分", "id": "440010"},
    {"pref": "Oita", "city": "中津", "id": "440020"},
    {"pref": "Oita", "city": "日田", "id": "440030"},
    {"pref": "Oita", "city": "佐伯", "id": "440040"},
    {"pref": "Miyazaki", "city": "宮崎", "id": "450010"},
    {"pref": "Miyazaki", "city": "延岡", "id": "450020"},
    {"pref": "Miyazaki", "city": "都城", "id": "450030"},
    {"pref": "Miyazaki", "city": "高千穂", "id": "450040"},
    {"pref": "Kagoshima", "city": "鹿児島", "id": "460010"},
    {"pref": "Kagoshima", "city": "鹿屋", "id": "460020"},
    {"pref": "Kagoshima", "city": "種子島", "id": "460030"},
    {"pref": "Kagoshima", "city": "名瀬", "id": "460040"},
    {"pref": "Okinawa", "city": "那覇", "id": "471010"},
    {"pref": "Okinawa", "city": "名護", "id": "471020"},
    {"pref": "Okinawa", "city": "久米島", "id": "471030"},
    {"pref": "Okinawa", "city": "南大東", "id": "472000"},
    {"pref": "Okinawa", "city": "宮古島", "id": "473000"},
    {"pref": "Okinawa", "city": "石垣島", "id": "474010"},
    {"pref": "Okinawa", "city": "与那国島", "id": "474020"},
]


class Location(BaseModel):
    prefecture: str = Field(alias="pref")
    city: str
    id_: str = Field(alias="id")


class Temperature(BaseModel):
    celsius: str | None
    fahrenheit: str | None


class TemperatureRange(BaseModel):
    min: Temperature
    max: Temperature


class WeatherDetail(BaseModel):
    weather: str
    wind: str
    wave: str


class WeatherImage(BaseModel):
    title: str
    url: str
    width: int
    height: int


class ChanceOfRain(BaseModel):
    T00_06: str
    T06_12: str
    T12_18: str
    T18_24: str


class WeatherForecast(BaseModel):
    date: str
    date_label: str = Field(alias="dateLabel")
    telop: str
    detail: WeatherDetail = Field(alias="detail")
    temperature: TemperatureRange
    chance_of_rain: ChanceOfRain = Field(alias="chanceOfRain")

    def format_forecast(self) -> str:
        return f"""
            Daet: {self.date}
            TemperatureMin: {self.temperature.min.celsius}度
            TemperatureMax: {self.temperature.max.celsius}度
            ChanceOfRain(00_06): {self.chance_of_rain.T00_06}
            ChanceOfRain(06_12): {self.chance_of_rain.T06_12}
            ChanceOfRain(12_18): {self.chance_of_rain.T12_18}
            ChanceOfRain(18_24): {self.chance_of_rain.T18_24}
            """


async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def convert_pref_to_id(prefecture: str) -> Location | None:
    locations = [Location(**d) for d in location_data]
    location_in_prefecture = [l for l in locations if l.prefecture == prefecture]
    if len(location_in_prefecture) == 0:
        return None
    else:
        return location_in_prefecture[0]


@mcp.tool()
async def get_forecast(prefecture: str) -> str:
    """
    Get forecast for a location in Japan

    Args:
        prefecture: Name of the prefecture of Japan (in English alphabets, e.g.) "Hokkaido", "Tokyo", "Osaka", etc.)
    """
    location = convert_pref_to_id(prefecture=prefecture)
    if location is None:
        return "Unable to locate"
    url = f"https://weather.tsukumijima.net/api/forecast?city={location.id_}"
    res = await make_nws_request(url=url)

    if not res:
        return "Unable to fetch forecast data for this location."
    forecasts = [WeatherForecast(**f) for f in res["forecasts"]]
    return "\n------\n".join([f.format_forecast() for f in forecasts])


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
