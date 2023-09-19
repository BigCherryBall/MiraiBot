class Team:
    Black = '黑'
    Red = '红'


class Turn:
    Black = '黑'
    Red = '红'


class MapStyle:
    default = 'default'
    flower_dancer = '花时舞者-绫华'
    mao_mao = '清凉夏日-猫羽雫'
    chang_e = '拒霜思-嫦娥'


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
        else:
            return ''
            

    @staticmethod
    def toString() ->str :
        return "[默认，清凉一夏-猫羽雫，花时舞者-绫华，拒霜思-嫦娥]"


class ChessStyle:
    default = 'default'
