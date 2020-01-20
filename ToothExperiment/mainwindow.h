#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

class QVBoxLayout;
class QSpinBox;
class QPushButton;

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = 0);
    ~MainWindow();
private:
    QSpinBox *redLowBox;
    QSpinBox *redHighBox;
    QSpinBox *greenLowBox;
    QSpinBox *greenHighBox;
    QSpinBox *blueLowBox;
    QSpinBox *blueHighBox;

    /*QLineEdit *redLowEdit;
    QLineEdit *greenLowEdit;
    QLineEdit *blueLowEdit;
    QLineEdit *redHighEdit;
    QLineEdit *greenHighEdit;
    QLineEdit *blueHighEdit;*/
    QPushButton *addImageButton;
    QPushButton *recalculateButton;
    QVBoxLayout *teethLayout;

    void processAddImageClick();
    void addImage(QImage &&image);
    void recalculate();
};

#endif // MAINWINDOW_H
