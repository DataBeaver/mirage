pragma Singleton
import QtQuick 2.7

QtObject {
    id: style

    readonly property QtObject fontSize: QtObject {
        property int smallest: 6
        property int smaller: 8
        property int small: 12
        property int normal: 16
        property int big: 24
        property int bigger: 32
        property int biggest: 48
    }

    readonly property QtObject fontFamily: QtObject {
        property string sans: "SFNS Display"
        property string serif: "Roboto Slab"
        property string mono: "Hack"
    }

    readonly property QtObject colors: QtObject {
        property color background0: Qt.hsla(0, 0, 0.8, 0.5)
        property color background1: Qt.hsla(0, 0, 0.8, 0.7)
        property color foreground: "black"
        property color foregroundDim: Qt.hsla(0, 0, 0.2, 1)
        property color foregroundError: Qt.hsla(0.95, 0.64, 0.32, 1)
    }

    property int radius: 5

    readonly property QtObject sidePane: QtObject {
        property color background: colors.background1
    }

    readonly property QtObject chat: QtObject {
        readonly property QtObject roomHeader: QtObject {
            property color background: colors.background1
        }

        readonly property QtObject roomEventList: QtObject {
            property color background: "transparent"
        }

        readonly property QtObject message: QtObject {
            property color background: colors.background1
            property color body: colors.foreground
            property color date: colors.foregroundDim
        }

        readonly property QtObject event: QtObject {
            property color background: colors.background1
            property real saturation: 0.22
            property real lightness: 0.24
            property color date: colors.foregroundDim
        }

        readonly property QtObject daybreak: QtObject {
            property color background: colors.background1
            property color foreground: colors.foreground
            property int radius: style.radius
        }

        readonly property QtObject inviteBanner: QtObject {
            property color background: colors.background1
        }

        readonly property QtObject leftBanner: QtObject {
            property color background: colors.background1
        }

        readonly property QtObject typingUsers: QtObject {
            property color background: colors.background0
        }

        readonly property QtObject sendBox: QtObject {
            property color background: colors.background1
        }
    }

    readonly property QtObject box: QtObject {
        property color background: colors.background1
        property int radius: style.radius
    }

    readonly property QtObject avatar: QtObject {
        property int radius: style.radius
        property color letter: "white"

        readonly property QtObject background: QtObject {
            property real saturation: 0.22
            property real lightness: 0.5
            property real alpha: 1
            property color unknown: Qt.hsla(0, 0, 0.22, 1)
        }
    }

    readonly property QtObject displayName: QtObject {
        property real saturation: 0.32
        property real lightness: 0.3
    }
}