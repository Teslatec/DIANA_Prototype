<!DOCTYPE html>
<html lang="ru">
<head>
   <!--   page meta settings   -->
   <?php require_once 'header/metahead.php'; ?>
   <title>CHARTS</title>
   <!--   additional CSS styles   -->
   <style type="text/css"></style>
</head>
<body>
<!--   забивка пространства   -->
   <header class="header">
      <div class="row header__back" style="margin:0 auto;height:50px;width:100%;"></div>
   </header>
<!--   забивка пространства   -->



  <!--   ОСНОВНОЙ БЛОК   -->
   <div class="container main">
      <!-- left block -->
      <div class="col-xs-8 left_block">
                  <!-- first title row -->
                  <div class="row left_block_1">
                     <h5><!--There will be name and hashsum--></h5>
                  </div>
                  <!-- doughnut chart and select row -->
                  <div class="row left_block_2">
                           <img src="img/1.svg" alt="" id="chartselect1img">
                           <img src="img/2.svg" alt="" id="chartselect2img">
                           <img src="img/3.svg" alt="" id="chartselect3img">
                           <!-- doughnut chart block -->
                           <div class="col-xs-6 left_block_col1">
                              <div class="row" style="height:23px;">
                                 <h4 style="margin-top: 9px;font-size: 14px;">Индекс гигиены</h4>
                              </div>
                              <div class="row" style="height:175px;margin: 10px auto 0;">
                                 <canvas id="myChart"></canvas>
                              </div>
                              <div class="donut-inner"><h5><?= $longterm_index ?>%</h5></div>
                           </div>
                           <!-- select row -->
                           <div class="col-xs-6 left_block_col2">
                              <div class="row" style="height:36px;">
                                 <h4 style="line-height: 34px; font-size: 14px;">Группа риска</h4>
                              </div>
                              <div class="row chartselect">
                                 <!-- red select row -->
                                 <div class="row chartselect3" id="chartselect3">
                                    <div class="col-xs-3" id="chartselect3round">
                                       <h2 style="margin: 5px auto;line-height: 35px;">3</h2>
                                    </div>
                                    <div class="col-xs-9" style="padding: 5px 10px;height: 45px;">
                                       <h4 style="font-size: 14px;text-align:left;line-height: 20px;">Высокий риск</h4>
                                       <p style="line-height: 8px;">заболеваний полости рта</p>
                                    </div>
                                 </div>
                                 <!-- yellow select row -->
                                 <div class="row chartselect2" id="chartselect2">
                                    <div class="col-xs-3" id="chartselect2round">
                                       <h2 style="margin: 5px auto;line-height: 35px;">2</h2>
                                    </div>
                                    <div class="col-xs-9" style="padding: 5px 10px;height: 45px;">
                                       <h4 style="font-size: 14px;text-align:left;line-height: 20px;">Средний риск</h4>
                                       <p style="line-height: 8px;">заболеваний полости рта</p>
                                    </div>
                                 </div>
                                 <!-- green select row -->
                                 <div class="row chartselect1" id="chartselect1">
                                    <div class="col-xs-3" id="chartselect1round">
                                       <h2 style="margin: 5px auto;line-height: 35px;">1</h2>
                                    </div>
                                    <div class="col-xs-9" style="padding: 5px 10px;height: 45px;">
                                       <h4 style="font-size: 14px;text-align:left;line-height: 20px;">Низкий риск</h4>
                                       <p style="line-height: 8px;">заболеваний полости рта</p>
                                    </div>

                                 </div>
                              </div>
                           </div>
                  </div>
                  <!-- decription of barchart -->
                  <div class="row" style="height:40px;">
                       <div class="row" style="height:23px;">
                          <p style="font-size:12px;padding-left:10px;">Оценка времени образования зубного налёта:</p>
                       </div>
                       <div class="row" style="padding:0 0 0 10px;">
                           <div class="col-xs-3" style="width:163.3px;">
                              <div class="col-xs-2" style="height:15px;width:10px;background:#9400d3;margin:0;padding:0;"></div>
                              <div class="col-xs-10" style="border-bottom:2px solid #9400d3;height:15px;width:153px;">
                                 <p style="line-height: 12px;margin-left: 5px;font-size:10px;"><?= $longterm_index ?>% - более недели</p>
                              </div>
                           </div>
                           <div class="col-xs-3" style="width:163.3px;">
                              <div class="col-xs-2" style="height:15px;width:10px;background:#ff99ff;margin:0;padding:0;"></div>
                              <div class="col-xs-10" style="border-bottom:2px solid #ff99ff;height:15px;width:153px;">
                                 <p style="line-height: 12px;margin-left: 5px;font-size:10px;"><?= $daily_index ?>% - сутки</p>
                              </div>
                           </div>
                           <div class="col-xs-3" style="width:163.3px;">
                              <div class="col-xs-2" style="height:15px;width:10px;background:#cccccc;margin:0;padding:0;"></div>
                              <div class="col-xs-10" style="border-bottom:2px solid #cccccc;height:15px;width:153px;">
                                 <p style="line-height: 12px;margin-left: 5px;font-size:10px;"><?= $pure_index ?>% - чисто</p>
                              </div>
                           </div>
                       </div>
                  </div>
                  <!-- barchart and text block -->
                  <div class="row" style="height:250px;">
                     <div class="col-xs-6" style="height:250px;width:230px;margin:0 30px 0 10px;">
                        <h4 style="margin: 15px auto 10px 40px;font-size:14px;">История наблюдений</h4>

                        <div class="bar-leftblock">
                           <h5 class="odd">100%</h5>
                           <h5>90%</h5>
                           <h5 class="odd">80%</h5>
                           <h5>70%</h5>
                           <h5 class="odd">60%</h5>
                           <h5>50%</h5>
                           <h5 class="odd">40%</h5>
                           <h5>30%</h5>
                           <h5 class="odd">20%</h5>
                           <h5>10%</h5>
                           <h5 class="odd">0%</h5>
                        </div>
                        <div class="row barchart" style="width:230px;height:200px;margin:0 auto;">
                           <canvas id="myChart2"></canvas>
                           <div class="bar-under"><h5><?= date("d/m/Y", $timestamp) ?></h5></div>

                        </div>
                        <div class="bar-inner" id="bar-inner"><h5><?= $longterm_index ?>%</h5></div>
                     </div>
                     <div class="col-xs-6" style="height:250px;width:230px;margin: 0;">
                        <h4 style="margin: 15px auto 10px;font-size:14px;">Группа риска №<?= $category_id ?></h4>
                        <?php switch ($category_id) : case 1: ?>
                           <p class="riskgroup_p">
                              Количество зубного налёта менее 15%.
                              Низкая вероятность возникновения заболевания полости рта.
                           </p>
                        <?php break; case 2 : ?>
                           <p class="riskgroup_p">
                              Количество зубного налёта от 16% до 50%.
                              Средняя вероятность возникновения заболевания полости рта.
                           </p>
                        <?php break; case 3 : ?>
                           <p class="riskgroup_p">
                              Количество зубного налёта более 50%.
                              Высокая вероятность возникновения заболевания полости рта.
                           </p>
                        <?php break; endswitch; ?> 
                     </div>
                  </div>
                  <!-- upperlined text row -->
                  <div class="row row13">
                     <p>Результаты расчёта не являются диагнозом
                        или медицинской рекомендацией и не
                        исключают консультации с врачом</p>
                  </div>
            </div>
      <!-- right block -->
      <div class="col-xs-4 right_block">
                  <!-- first row with date/time -->
                  <div class="row right_block_1">
                     <h4><?= date("d.m.Y / H:i:s", $timestamp) ?></h4>
                  </div>
                  <!-- three image's rows -->
                  <div class="row right_block_2">
                     <img src="img/img.jpg" alt="" class="imageblock">
                  </div>
                  <div class="row right_block_3">
                     <img src="img/img.jpg" alt="" class="imageblock">
                  </div>
                  <div class="row right_block_4">
                     <img src="img/img.jpg" alt="" class="imageblock">
                  </div>
                  <!-- upperlined text row -->
                  <div class="row right_block_5">
                     <p>Identified by Diana&trade; – Dental Index Analysis Application</p>
                  </div>
            </div>
   </div>
   <!--   ОСНОВНОЙ БЛОК   -->
</body>
<!--   .JS, script & etc   -->
<?php require_once 'header/metafoot.php'; ?>
</html>
