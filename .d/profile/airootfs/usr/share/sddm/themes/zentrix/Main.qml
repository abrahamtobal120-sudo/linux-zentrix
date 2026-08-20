import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#0a0d12"

    property color panelColor: "#1a202b"
    property color textColor: "#e5e7eb"
    property color accentColor: "#1f8bff"

    Image {
        anchors.fill: parent
        source: "file:///usr/share/wallpapers/zentrix-dark.png"
        fillMode: Image.PreserveAspectCrop
        smooth: true
    }

    Rectangle {
        anchors.fill: parent
        color: "#090c11"
        opacity: 0.86
    }

    ColumnLayout {
        anchors.centerIn: parent
        width: Math.min(parent.width * 0.86, 760)
        spacing: 16

        Image {
            Layout.alignment: Qt.AlignHCenter
            source: "file:///usr/share/zentrix/logos/zentrix-sddm-logo.png"
            width: Math.min(420, parent.width * 0.7)
            height: width * 0.35
            fillMode: Image.PreserveAspectFit
            smooth: true
            cache: false
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "Zentrix"
            color: textColor
            font.pixelSize: 34
            font.bold: true
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "by Abraham Tobal"
            color: "#9fb0c7"
            font.pixelSize: 17
        }

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 8
            width: Math.min(540, parent.width)
            radius: 14
            color: panelColor
            border.color: "#2d3748"
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 12

                Text {
                    Layout.fillWidth: true
                    text: Qt.formatDateTime(new Date(), "dddd, dd MMM yyyy  HH:mm")
                    color: "#b6c4d8"
                    horizontalAlignment: Text.AlignHCenter
                    font.pixelSize: 15
                }

                TextField {
                    id: userField
                    Layout.fillWidth: true
                    placeholderText: "User"
                    text: userModel.lastUser || "zentrix"
                    color: textColor
                    selectionColor: accentColor
                }

                TextField {
                    id: passwordField
                    Layout.fillWidth: true
                    placeholderText: "Password"
                    echoMode: TextInput.Password
                    color: textColor
                    selectionColor: accentColor
                    onAccepted: loginButton.clicked()
                }

                ComboBox {
                    id: sessionBox
                    Layout.fillWidth: true
                    model: sessionModel
                    textRole: "name"
                }

                Button {
                    id: loginButton
                    Layout.fillWidth: true
                    text: "Sign In"
                    onClicked: sddm.login(userField.text, passwordField.text, sessionBox.currentIndex)
                }

                Text {
                    id: errorLabel
                    Layout.fillWidth: true
                    color: "#f87171"
                    text: sddm.loginErrorMessage
                    visible: text.length > 0
                    wrapMode: Text.WordWrap
                }
            }
        }

        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 8
            spacing: 10

            Button {
                text: "Suspend"
                enabled: sddm.canSuspend
                visible: sddm.canSuspend
                onClicked: sddm.suspend()
            }

            Button {
                text: "Restart"
                enabled: sddm.canReboot
                visible: sddm.canReboot
                onClicked: sddm.reboot()
            }

            Button {
                text: "Power Off"
                enabled: sddm.canPowerOff
                visible: sddm.canPowerOff
                onClicked: sddm.powerOff()
            }
        }
    }
}
