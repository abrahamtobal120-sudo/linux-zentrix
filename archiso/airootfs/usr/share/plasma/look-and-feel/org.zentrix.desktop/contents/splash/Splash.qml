import QtQuick 2.15

Rectangle {
    id: root
    width: 1920
    height: 1080
    color: "#070a0f"

    Image {
        anchors.fill: parent
        source: "file:///usr/share/wallpapers/zentrix-dark.svg"
        fillMode: Image.PreserveAspectCrop
        smooth: true
    }

    Rectangle {
        anchors.fill: parent
        color: "#05070b"
        opacity: 0.20
    }

    Column {
        anchors.centerIn: parent
        spacing: 22

        Image {
            anchors.horizontalCenter: parent.horizontalCenter
            source: "file:///usr/share/zentrix/logos/zentrix-plymouth-logo.png"
            width: Math.min(root.width * 0.24, 360)
            height: 140
            fillMode: Image.PreserveAspectFit
            smooth: true
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "ZENTRIX OS"
            color: "#f8fafc"
            font.pixelSize: 48
            font.bold: true
            font.letterSpacing: 5
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "Iniciando..."
            color: "#9fb0c7"
            font.pixelSize: 16
            font.letterSpacing: 2
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: 220
            height: 3
            radius: 2
            color: "#172033"

            Rectangle {
                id: progress
                height: parent.height
                width: parent.width * 0.35
                radius: 2
                color: "#60a5fa"
                x: 0

                SequentialAnimation on x {
                    loops: Animation.Infinite
                    NumberAnimation { from: 0; to: 143; duration: 900; easing.type: Easing.InOutQuad }
                    NumberAnimation { from: 143; to: 0; duration: 900; easing.type: Easing.InOutQuad }
                }
            }
        }
    }
}
