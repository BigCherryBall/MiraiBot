class Team:
    Black = '黑'
    Red = '红'


class Turn:
    Black = '黑'
    Red = '红'


class MapStyle:
    default = '默认'
    flower_dancer = '花时舞者-绫华'
    mao_mao = '清凉夏日-猫羽雫'
    chang_e = '拒霜思-嫦娥'
    zhong_wu_yan1 = '超时空战士-钟无艳'
    zhong_wu_yan2 = '王者之锤-钟无艳'

    @staticmethod
    def getStyle(name: str) -> str:
        if name == MapStyle.mao_mao:
            return MapStyle.mao_mao
        elif name == MapStyle.flower_dancer:
            return MapStyle.flower_dancer
        elif name == MapStyle.default:
            return MapStyle.default
        elif name == MapStyle.chang_e:
            return MapStyle.chang_e
        elif name == MapStyle.zhong_wu_yan1:
            return MapStyle.zhong_wu_yan1
        elif name == MapStyle.zhong_wu_yan2:
            return MapStyle.zhong_wu_yan2
        else:
            return ''

    @staticmethod
    def toString() -> str:
        return "[默认，清凉夏日-猫羽雫，花时舞者-绫华，拒霜思-嫦娥，超时空战士-钟无艳，王者之锤-钟无艳]"


class ChessStyle:
    default = 'default'
