// SPDX-License-Identifier: LGPL-3.0-or-later

import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12
import "../.."
import "../../Base"

HFlickableColumnPage {
    id: accountSettings
    title: qsTr("Account settings")
    header: HPageHeader {}


    property int avatarPreferredSize: 256 * theme.uiScale

    property string userId: ""

    readonly property bool ready:
        accountInfo !== null && accountInfo.profile_updated > new Date(1)

    readonly property QtObject accountInfo:
        ModelStore.get("accounts").find(userId)

    property string headerName: ready ? accountInfo.display_name : userId


    HSpacer {}

    Repeater {
        id: repeater
        model: ["Profile.qml", "ImportExportKeys.qml"]

        Rectangle {
            color: ready ? theme.controls.box.background : "transparent"
            Behavior on color { HColorAnimation {} }

            Layout.alignment: Qt.AlignCenter
            Layout.topMargin: index > 0 ? theme.spacing : 0
            Layout.bottomMargin: index < repeater.count - 1 ? theme.spacing : 0

            Layout.maximumWidth: Math.min(parent.width, 640)
            Layout.preferredWidth:
                pageLoader.isWide ? parent.width : avatarPreferredSize

            Layout.preferredHeight: childrenRect.height

            HLoader {
                anchors.centerIn: parent
                width: ready ? parent.width : 96
                source: ready ?
                        modelData :
                        (modelData === "Profile.qml" ?
                         "../../Base/HBusyIndicator.qml" : "")
            }
        }
    }

    HSpacer {}
}
