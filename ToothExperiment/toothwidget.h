#ifndef TOOTHWIDGET_H
#define TOOTHWIDGET_H

#include <QWidget>
#include <QImage>

class QLabel;

class ToothWidget : public QWidget
{
    Q_OBJECT
public:
    explicit ToothWidget(QImage &&image, QWidget *parent = nullptr);
    double update(int redLow, int redHigh,
                int greenLow, int greenHigh,
                int blueLow, int blueHigh);
private:
    QImage originalImage;
    QImage processedImage;

    QLabel *originalLabel;
    QLabel *processedLabel;
    QLabel *dirtynessLabel;

    double recalculate(int redLow, int redHigh,
                       int greenLow, int greenHigh,
                       int blueLow, int blueHigh);
};

#endif // TOOTHWIDGET_H
