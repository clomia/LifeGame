# [단위=1세대당 field]그리드 연속연산량
FIRST_PROPHECY_COUNT: int = 100  # 첫 연산량
PROPHECY_COUNT: int = 1000
# [단위:초]메인프로세스-연산쓰레드의 연산,데이터 제공 간격
FIRST_OPERATION_SPEED: int = 10  # 첫 연산 이후의 간격
OPERATION_SPEED: int = 500
# CacheManagementPipe가 사용합니다. 현재 연산제공이 (limit=50)회를 넘어서면 SLOW_OPERATION_SPEED만큼 연산간격을 지연시킵니다.
SLOW_OPERATION_SPEED: int = 1000
# 연산프로세스의 prophecy 클래스가 스스로 저장하는 메모리, simul프로세스가 연산을 제공받아서 저장하는 메모리가 과부화되는것을 예방합니다.
""" 
Todo: 위 시스템을 개선해야 한다 -나에게 보내는 메세지-
현재 상수가 적용되면 연산사용량이 최대일때(초당 1세대를 소비할때) simul프로세스의 메모리량은 산 모양의 그래프를 그립니다.
CacheManagementPipe가 작동할때가 되면 대략 25000세대정보가 여유분으로 남게되며 (매번 500세대씩 남는게 50번 반복되므로)
CacheManagementPipe가 작동한 이후 정보의 여유분이 사라지기까지 대략 10만세대 이상 이터레이션 할 수 있습니다. (매번 500세대씩 부족한 제공이 50번 반복되므로)
가장 최적이라고 생각되는 상수를 적용한 결과(예상)입니다.

이런 연산 제공방식은 개선이 필요합니다. 시간 간격에 의존하는것이 아니라,
simul 게임로직쪽에서 연산요청을 보내고 그것에 응답하는 방식으로 진행되어야 합니다.
용량을 알 수 있는 Queue상속 클래스를 구현해서 용량이 부족해지면 스스로 정보 요청신호를 보내도록 설계해야 합니다.
일단 보류중이지만 반드시 개선하고 이 글을 지워주세요
"""
# -------------------------------
SIGNAL = object()
PROPHECY_REQUEST = "prophecy".encode("utf-8")
BPRIN_BOOTING_REQUEST = "bprin,booting".encode("utf-8")
PROPHECY_COMPLETE_SIGNAL = "prophecy,complete".encode("utf-8")
# -------------------------------
# todo 여기서 포트번호 검사 & 설정하기
BPRIN_PROC_PORT: int = 40000
SIMUL_PROC_PORT: int = 40001
