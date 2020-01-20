#include "mainwindow.h"
#include "toothwidget.h"

#include <QSpinBox>
#include <QGridLayout>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QWidget>
#include <QPushButton>
#include <QFileDialog>
#include <QImage>
#include <QScrollArea>

#include <QDebug>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    addImageButton = new QPushButton(tr("Add image"), this);
    connect(addImageButton, &QPushButton::clicked, this, &MainWindow::processAddImageClick);

    redLowBox = new QSpinBox(this);
    redHighBox = new QSpinBox(this);
    greenLowBox = new QSpinBox(this);
    greenHighBox = new QSpinBox(this);
    blueLowBox = new QSpinBox(this);
    blueHighBox = new QSpinBox(this);

    auto spinboxes = {redLowBox, redHighBox,
                      greenLowBox, greenHighBox,
                      blueLowBox, blueHighBox};
    for (auto spinbox : spinboxes) {
        spinbox->setMinimum(0);
        spinbox->setMaximum(255);
    }

    redLowBox->setValue(3);
    redHighBox->setValue(186);
    greenLowBox->setValue(17);
    greenHighBox->setValue(75);
    blueLowBox->setValue(37);
    blueHighBox->setValue(160);

    for (auto spinbox : spinboxes) {
        connect(spinbox, QOverload<int>::of(&QSpinBox::valueChanged),
                this, &MainWindow::recalculate);
    }

    QGridLayout *rgbLayout = new QGridLayout();
    rgbLayout->addWidget(redLowBox, 0, 0);
    rgbLayout->addWidget(redHighBox, 0, 1);
    rgbLayout->addWidget(greenLowBox, 1, 0);
    rgbLayout->addWidget(greenHighBox, 1, 1);
    rgbLayout->addWidget(blueLowBox, 2, 0);
    rgbLayout->addWidget(blueHighBox, 2, 1);

    recalculateButton = new QPushButton(tr("Recalculate"), this);
    connect(recalculateButton, &QPushButton::clicked, this, &MainWindow::recalculate);

    QHBoxLayout *headerLayout = new QHBoxLayout();
    headerLayout->addWidget(addImageButton);
    headerLayout->addItem(rgbLayout);
    headerLayout->addWidget(recalculateButton);

    teethLayout = new QVBoxLayout();
    QWidget *teethWidget = new QWidget(this);
    teethWidget->setLayout(teethLayout);
    QScrollArea *teethArea = new QScrollArea(this);
    teethArea->setWidgetResizable(true);
    teethArea->setWidget(teethWidget);
    teethArea->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Expanding);

    QVBoxLayout *mainLayout = new QVBoxLayout();
    mainLayout->addItem(headerLayout);
    mainLayout->addWidget(teethArea);

    QWidget *mainWidget = new QWidget(this);
    mainWidget->setLayout(mainLayout);

    setCentralWidget(mainWidget);
}

MainWindow::~MainWindow()
{

}

void MainWindow::processAddImageClick()
{
    QStringList filenames = QFileDialog::getOpenFileNames(this, tr("Add images"), QString(),
                                                          tr("Image Files (*.png *.jpg *.bmp *.PNG *.JPG *.BMP)"));
    for (const auto &filename : filenames) {
        QImage image(filename);
        qDebug() << filename;
        addImage(std::move(image));
    }

    recalculate();
}

void MainWindow::addImage(QImage &&image)
{
    ToothWidget *toothWidget = new ToothWidget(std::move(image), this);
    toothWidget->setVisible(true);
    teethLayout->addWidget(toothWidget);
}

void MainWindow::recalculate()
{
    int rLow = redLowBox->value();
    int rHigh = redHighBox->value();
    int gLow = greenLowBox->value();
    int gHigh = greenHighBox->value();
    int bLow = blueLowBox->value();
    int bHigh = blueHighBox->value();

    double dirtynessSum = 0.0;
    int count = 0;

    for (int i = 0; i < teethLayout->count(); i++) {
        QWidget *widget = teethLayout->itemAt(i)->widget();
        if (!widget) {
            continue;
        }

        ToothWidget *toothWidget = qobject_cast<ToothWidget *>(widget);
        if (!toothWidget) {
            continue;
        }

        double dirtyness = toothWidget->update(rLow, rHigh, gLow, gHigh, bLow, bHigh);
        dirtynessSum += dirtyness;
        count++;
    }

    double averageDirtyness = dirtynessSum / count;
    qDebug() << "Total dirtyness" << averageDirtyness;
}
