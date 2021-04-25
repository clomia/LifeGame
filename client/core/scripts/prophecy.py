"""
라이프 게임 시뮬레이션 연산 모듈입니다.
"""
from __future__ import annotations
from typing import Dict, Tuple, Union, Callable, Set, List, Mapping
from collections.abc import Mapping
from collections import defaultdict
from itertools import chain, permutations

# 좌표값 x,y는 항상 튜플이어야 한다
Co = Tuple[int, int]
Delta = Dict[Co, int]
# (세포의 존재여부 , 주변 세포의 갯수) -> 다음 세대에 세포 존재여부 반환
Logic = Callable[[int, int], int]


class ProphecyExeption(Exception):
    """ 모듈의 최상위 예외"""


class ProphecyIndexError(ProphecyExeption):
    """ 소실점으로 제한된 시간 범위를 벗어난 세대 인덱스를 검색할때 발생"""


class Space(dict):
    """
    값이 없는 좌표를 받으면 0을 반환한다.

    defaultdict와 다르게 0을 저장하지 않는다.

    state 메서드를 사용해 {세포값:갯수} 를 알아 낼 수 있다
    """

    def __missing__(self, key):
        return 0

    def __repr__(self) -> str:
        return f"<Space {super().__repr__()}>"

    def __str__(self) -> str:
        return f"<Space {super().__repr__()}>"

    def state(self) -> defaultdict:
        """ 살아있는 세포들의 종류별 갯수를 반환한다."""

        result = defaultdict(lambda: 0)
        for cell in self.values():
            result[cell] += 1
        return result


class PropheticGrid(Mapping):
    """
    [주의!]객체는 멸망점의 space와 delta를 가지지 않는다 멸망점 이전 세대까지만 이터레이션 한다

    객체의 정의: 무한한 크기의 그리드(공간)와 소실점까지의 시간을 곱한것

    ---
    Special Method
    ---
    인스턴스를 (ins)라고 표기한다

    for delta in (ins) : 시작점부터 Delta를 이터레이션한다.
    for delta in -(ins) : 종단점~시작점까지 시간을 역행할수 있는 Delta를 이터레이션한다.
    (ins)[x] : x세대의 Space를 반환한다. / (ins)[x,y] x~(y-1)까지의 세대를 반환한다.
    ~(ins) : Field을 얼려서 반환한다.
    -(ins) : 시간을 뒤집어서 반환한다. 이 영향으로 Field이 얼게된다.
    len(int) : 소멸점 까지 걸리는 세대를 반환한다. 소멸점을 모르는 동안에는 0을 반환한다.

    Field 추출 , 시간역행 , Field얼리기 등 얼마든지 조합해서 구현할수 있다.

    ---
    사용되는 개념 (변수명)
    ---
    Cell: 세포의 상태이다. 양의정수이며 0은 없음,1부터는 세포의 색(팀) 구분자이다.
    Space: 공간(그리드)이다. 크기가 무한하다. 딕셔너리를 상속받아서 구현되었다.
    Delta: 공간의 변화이다. 다음 세대로 공간이 변화하는데에 필요한 최소한의 정보만 담은 dict이다.
    Logic: 생명게임의 규칙이다. 자기 자신의 Cell값과 주변8칸의 Cell값을 가지고 다음 세대에 자신이 가져야 할 Cell값을 반환한다.
    Field: 시공간을 의미한다 Space와 Delta들을 묶어서 field라고 한다.

    시작점: 생성자가 입력받는 Space를 의미한다.
    종단점: 객채가 알고있는 가장 먼 미래의 Space이다 (객체의 관점은 항상 시작점이다).
    소실점: 텅 빈 Space를 의미한다.

    Field을 얼리다: 종단점 이후를 소실점으로 만들어서 고정한다. 시작과 끝을 모두 알고있는 상태로 만든다.

    ---
    주의사항
    ---
    객체의 기능: 무한한 시공간을 시뮬레이션\n
    위 기능을 실현시키기 위해서 최소한의 연산만 수행하는 알고리즘이 구현되었습니다.\n
    시간 연산: 연산이 필요할 때에만 연산을 하고 그 결과를 캐싱(저장)합니다.\n
    공간 연산: 무한한 공간에서 가변좌표만 추출 한 뒤 연산합니다. (가변좌표: 다음 세대에 변화 가능성이 있는 좌표)

    이 사항을 충분히 고려하지 않으면 예상치 못한 곳에서 많은 시간을 소모할 수 있습니다.

    ---
    예시
    ---
    객체를 생성하자마자(무정보상태) (ins)[20] 을 사용해 20번째 세대의 공간을 구해봅시다.\n
    값을 구하기 위해서 20세대까지 시공간(시뮬레이션) 연산을 실행합니다.\n
    수십 세대의 시공간 연산은 방대한 작업이기 때문에 연산 결과(시공간 정보)를 모두 캐시로 저장합니다.\n
    이제 이 객체를 1~30세대까지 이터레이션해봅시다.\n
    이터레이션 되면서 필요한 연산만(21~30세대) 추가 연산합니다.\n
    이 때문에 1~20세대까지는 매우 빠르게 이터레이션 되지만 21~30세대까지는 느리게 이터레이션 됩니다.\n
    이제 객체는 30세대까지의 데이터를 가지고 있습니다.
    """

    def LOGIC(cell: int, neighbors: List[int]) -> int:
        """ 좌표의 다음 cell값을 반환한다"""
        neighbor_count = len(neighbors)
        if cell:
            if neighbor_count == 2 or neighbor_count == 3:
                return cell
            else:
                return 0
        else:
            if neighbor_count == 3:
                if (cur_cell := neighbors.pop(0)) in neighbors:
                    return cur_cell
                else:
                    return neighbors[0]
            else:
                return 0

    @staticmethod
    def neighbors(co: Co, space: Space) -> List[int]:
        # 주변 8칸에 "존재하는" cell값들을 반환한다
        x, y = co
        neighbor_list = []
        for add_x, add_y in chain(permutations([-1, 0, 1], 2), ((1, 1), (-1, -1))):
            co = (x + add_x, y + add_y)
            if cell := space[co]:
                neighbor_list.append(cell)
        return neighbor_list

    @staticmethod
    def space(dictionary: Union[dict, Space] = {}) -> Space:
        """
        Space로 변환한다.

        1. dict를 받으면 Space로 변환.
        2. 인자가 없으면 빈 Space를 반환.
        3. Space를 받으면 그대로 반환.
        """
        if isinstance(dictionary, Space):
            return dictionary
        else:
            space_dict = Space()
            for key, value in dictionary.items():
                space_dict[key] = value
            return space_dict

    @staticmethod
    def variable_coordinates(space: Space) -> Set[Co]:
        """
        Space를 받아서 모든 가변좌표를 반환한다

        세포들의 주변 8개의 좌표들을 중복 없이(set으로) 반환한다
        """
        variable_cos = set()
        for x, y in space.keys():
            for add_x, add_y in chain(permutations([-1, 0, 1], 2), ((1, 1), (0, 0), (-1, -1))):
                co = (x + add_x, y + add_y)
                variable_cos.add(co)
        return variable_cos

    @staticmethod
    def delta(previous_space: Space, next_space: Space) -> Delta:
        """ Space 사이의 Delta를 반환한다"""
        delta_dict = {}
        for n_co, n_cell in next_space:
            if previous_space[n_co] != n_cell:
                delta_dict[n_co] = n_cell
        return delta_dict

    def __init__(self, start_info: Space, *, logic: Logic = LOGIC):
        """
        시작점을 입력받는다
        """
        self.logic = logic
        self.space_list, self.delta_list = [self.space(start_info)], [{}]
        self.length = lambda: len(self.space_list)

    def prophesy(self, space: Space) -> Tuple[Space, Delta]:
        """
        공간을 입력받아서 다음세대의 공간과 델타를 반환한다

        반환할 값을 space_list , delta_list에 캐싱한다.
        """
        next_space, next_delta = self.space(), {}
        variable_cos = self.variable_coordinates(space)
        for co in variable_cos:
            neighbor_list = self.neighbors(co, space)
            cell = space[co]
            next_cell = self.logic(cell, neighbor_list)
            if cell != next_cell:
                next_delta[co] = next_cell
            if next_cell:
                next_space[co] = next_cell
        self.space_list.append(next_space)
        self.delta_list.append(next_delta)
        return next_space, next_delta

    def execute(self):
        """ 다음 세대로 넘어간다"""
        return self.prophesy(self.space_list[-1])

    def __getitem__(self, generation: int):
        """
        (int)[x] 를 정의한다
        """
        try:
            return self.space_list[generation]
        except IndexError:
            iter_count = range(generation - self.length() + 1)
            for _ in iter_count:
                if not self.execute()[1]:
                    raise ProphecyIndexError("시간 범위를 벗어났습니다. 소멸점 밖의 세대입니다.")
            return self.__getitem__(generation)

    def __iter__(self):
        """
        이터레이션은 delta와 space를 반환합니다
        """
        yield from zip(self.delta_list, self.space_list)
        while True:
            next_space, next_delta = self.execute()
            if next_delta:
                yield (next_delta, next_space)
            else:
                break

    def __len__(self) -> int:
        """
        소실점까지의 걸리는 세대 수를 반환합니다.

        소실점을 모르면 0를 반환합니다.
        """
        if not self.delta_list[-1] and self.length != 1:
            return self.length()
        else:
            return 0

    def __neg__(self):
        """
        -object를 정의합니다

        시공간을 얼리고 뒤집어서 반환합니다.

        얼린다->시작점 이전(0세대)과 종단점 이후를 소실점으로 만들어서 시공간을 고정합니다\n
        뒤집는다-> 반환된 객체를 이터레이션하면 종단점에서 시작점으로 (과거로)역행합니다.
        """
        new_ins = PropheticGrid(self.space_list[-1])
        space_list = list(chain(reversed(self.space_list), [self.space_list[0]]))
        delta_list = [{}]
        previous_space = space_list[0]
        for next_space in space_list[1:]:
            delta_list.append(self.delta(previous_space, next_space))
            previous_space = next_space
        new_ins.space_list = space_list
        new_ins.delta_list = delta_list + [{}]
        return new_ins

    def __invert__(self):
        """
        ~object를 정의합니다

        객체를 얼려서 반환합니다.

        얼린다->시작점 이전(0세대)과 종단점 이후를 소실점으로 만들어서 시공간을 고정합니다.
        """
        new_ins = PropheticGrid(self.space_list[0])
        new_ins.space_list = self.space_list + [self.space_list[-1]]
        new_ins.delta_list = self.delta_list + [{}]
        return new_ins

    def __repr__(self) -> str:
        return f"<PropheticGridlength Cach={self.length()}, time={len(self)}, start_point={self.space_list[0]}, end_point={self.space_list[-1]}>"

    def __str__(self) -> str:
        return f"<PropheticGridlength  Cache={self.length()}>"


if __name__ == "__main__":
    """
    bprin = {}
    for i in range(225):
        if i % 2 == 0:
            bprin[(-i, i)] = 1
        else:
            bprin[(-i, i)] = 2
    print(f"FieldSet-> {bprin}")
    """
    infinity_pattern = {
        (1, 1): 1,
        (2, 2): 2,
        (3, 1): 1,
        (3, 2): 2,
        (4, 3): 1,
        (5, 1): 2,
        (5, 2): 1,
        (5, 3): 2,
        (5, 5): 1,
        (1, 4): 2,
        (1, 5): 1,
        (2, 5): 2,
        (3, 5): 1,
        (1001, 1): 1,
        (1002, 2): 2,
        (1003, 1): 1,
        (1003, 2): 2,
        (1004, 3): 1,
        (1005, 1): 2,
        (1005, 2): 1,
        (1005, 3): 2,
        (1005, 5): 1,
        (1001, 4): 2,
        (1001, 5): 1,
        (1002, 5): 2,
        (1003, 5): 1,
    }
    iterator = PropheticGrid(infinity_pattern)
    count = 0
    count_count = 0
    import time

    counter = int(input("이터레이션 횟수 입력: "))
    start = pre_now = time.time()
    for (delta, space), _ in zip(iterator, range(counter)):
        # print(delta)
        count += 1
        if count < 20:
            print(count + count_count * 20, end=",")
        else:
            now = time.time()
            time_delta = now - pre_now
            pre_now = now
            print(
                count + count_count * 20,
                f" || {count + count_count * 20}세대에서의 세포 갯수: {space.state()[1] + space.state()[2]}, 20세대 연산하는데 걸린 시간: {time_delta:.3f}초, 1세대 연산시간 평균: {time_delta/20:.4f}초",
            )
            count = 0
            count_count += 1
    finish = time.time()
    print(f"\n{counter}세대 이터레이션 하는데 걸린 시간: {finish-start}초")
    # print(f"마지막 delta={delta}")
    """ 
    1000번 이터레이션 
    평균 3.7초
    10000번 이터레이션
    178초 
    :위 패턴의 경우 세포 수가 70개로 시작해서 10000세대에에서는 2460개가 된다.
    """
