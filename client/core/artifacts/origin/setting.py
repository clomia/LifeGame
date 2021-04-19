""" 설정 관리 모듈 """
import json

with open("core/artifacts/origin/setting.json", "rt") as file:
    SETTING: dict = json.load(file)


def config(setting: dict):
    """ setting.json변경 함수 [주의!]add가 아니라 replace이다. 변경한 SETTING 딕셔너리를 입력하세요."""
    with open("core/artifacts/origin/setting.json", "wt") as file:
        json.dump(setting, file)


class Language:
    """ 언어전환을 동적으로 할 수 있도록 클래스로 구현"""

    def __init__(self):
        self.now: str = SETTING["language"]
        self.langs = ("ko", "en")

    def setting(self, lang):
        if not (lang in self.langs):
            raise Exception(f"{self.langs}안에서 입력하세요")
        self.now = lang
        SETTING["language"] = lang
        config(SETTING)


LANGUAGE = Language()


class GameConfig:
    """
    게임 벨런스에 큰 영향을 주는 변수 모음이다.
    벨런스 조정시 사용하는 클래스이다.

    변수명은 대문자 시작+'_'로 띄어쓰기
    """

    Bprin_Handicap_Count: int = 3
    IterStep_Count: int = 19
    Execution_Iter_Delay: int = 10


__all__ = ["LANGUAGE", "GameConfig"]
