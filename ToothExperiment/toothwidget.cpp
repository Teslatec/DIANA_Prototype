#include "toothwidget.h"

#include <QHBoxLayout>
#include <QLabel>

#include <QDebug>

ToothWidget::ToothWidget(QImage &&image, QWidget *parent) :
    QWidget(parent),
    originalImage(image),
    processedImage(image.size(), image.format())
{
    originalLabel = new QLabel(this);
    originalLabel->setPixmap(QPixmap::fromImage(originalImage));

    processedLabel = new QLabel(this);
    dirtynessLabel = new QLabel(this);

    QLayout *layout = new QHBoxLayout(this);
    layout->addWidget(originalLabel);
    layout->addWidget(processedLabel);
    layout->addWidget(dirtynessLabel);
    setLayout(layout);
}

double ToothWidget::update(int redLow, int redHigh,
                         int greenLow, int greenHigh,
                         int blueLow, int blueHigh)
{
    double dirtyness = recalculate(redLow, redHigh, greenLow,
                                   greenHigh, blueLow, blueHigh);
    processedLabel->setPixmap(QPixmap::fromImage(processedImage));
    dirtynessLabel->setText(QString::number(dirtyness));

    return dirtyness;
}

double ToothWidget::recalculate(int redLow, int redHigh, int greenLow, int greenHigh, int blueLow, int blueHigh)
{
    int dirtyCount = 0;
    int totalCount = 0;

    for (int y = 0; y < originalImage.height(); y++) {
        for (int x = 0; x < originalImage.width(); x++) {
            QRgb pixel = originalImage.pixel(x, y);
            QRgb outPixel = 0;
            int r = qRed(pixel);
            int g = qGreen(pixel);
            int b = qBlue(pixel);

            if (r == 255 && g == 255 && b == 255) {
                outPixel = qRgb(r, g, b);
            } else {
                if (r > redLow && r < redHigh &&
                    g > greenLow && g < greenHigh &&
                    b > blueLow && b < blueHigh) {
                    outPixel = qRgb(255, 0, 0);
                    dirtyCount++;
                } else {
                    outPixel = qRgb(r, g, b);
                }
                totalCount++;
            }

            processedImage.setPixel(x, y, outPixel);
        }
    }

    double dirtyness = double(dirtyCount) / double(totalCount);
    return dirtyness;
}
