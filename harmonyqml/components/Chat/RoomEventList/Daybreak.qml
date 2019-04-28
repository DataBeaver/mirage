import QtQuick 2.7
import "../../Base" as Base

Base.HNoticeLabel {
    text: dateTime.toLocaleDateString()
    color: Base.HStyle.chat.daybreak.foreground
    backgroundColor: Base.HStyle.chat.daybreak.background
    radius: Base.HStyle.chat.daybreak.radius
}