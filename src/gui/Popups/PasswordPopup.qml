// SPDX-License-Identifier: LGPL-3.0-or-later

import QtQuick 2.12
import QtQuick.Layouts 1.12
import "../Base"

BoxPopup {
    id: popup
    okEnabled: Boolean(passwordField.text)

    onAboutToShow: {
        okClicked         = false
        acceptedPassword  = ""
        passwordValid     = null
        errorMessage.text = ""
    }
    onOpened: passwordField.forceActiveFocus()


    signal cancelled()


    property bool validateWhileTyping: false

    property string acceptedPassword: ""
    property var passwordValid: null

    property alias field: passwordField


    function verifyPassword(pass, callback) {
        // Can be reimplemented when using this component.
        // Pass to the callback true on success, false on invalid password,
        // or a custom error message string.
        callback(true)
    }


    box.buttonCallbacks: ({
        ok: button => {
            const password    = passwordField.text
            okClicked         = true
            button.loading    = true
            errorMessage.text = ""

            verifyPassword(password, result => {
                if (result === true) {
                    passwordValid          = true
                    popup.acceptedPassword = password
                    popup.close()
                } else if (result === false) {
                    passwordValid = false
                } else {
                    errorMessage.text = result
                }

                button.loading = false
            })
        },
        cancel: button => {
            popup.close()
            cancelled()
        },
    })


    HRowLayout {
        spacing: theme.spacing

        Layout.fillWidth: true

        HTextField {
            id: passwordField
            echoMode: TextInput.Password
            focus: true
            error: passwordValid === false

            onTextChanged: passwordValid =
                validateWhileTyping ? verifyPassword(text) : null

            Layout.fillWidth: true
        }

        HIcon {
            visible: Layout.preferredWidth > 0
            svgName: passwordValid ? "ok" : "cancel"
            colorize: passwordValid ?
                      theme.colors.positiveBackground :
                      theme.colors.negativeBackground

            Layout.preferredWidth:
                passwordValid === null ||
                (validateWhileTyping && ! okClicked && ! passwordValid) ?
                0 :implicitWidth

            Behavior on Layout.preferredWidth { HNumberAnimation {} }
        }
    }

    HLabel {
        id: errorMessage
        wrapMode: Text.Wrap
        color: theme.colors.errorText

        visible: Layout.maximumHeight > 0
        Layout.maximumHeight: text ? implicitHeight : 0
        Behavior on Layout.maximumHeight { HNumberAnimation {} }

        Layout.fillWidth: true
    }
}
