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
                     <h5>Текст, текст, текст</h5>
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
                              <div class="donut-inner"><h5>99%</h5></div>
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
                                       <h4 style="font-size: 14px;text-align:left;line-height: 20px;">Текст текст текст </h4>
                                       <p style="line-height: 15px;">текст текст текст текст</p>
                                    </div>
                                 </div>
                                 <!-- yellow select row -->
                                 <div class="row chartselect2" id="chartselect2">
                                    <div class="col-xs-3" id="chartselect2round">
                                       <h2 style="margin: 5px auto;line-height: 35px;">2</h2>
                                    </div>
                                    <div class="col-xs-9" style="padding: 5px 10px;height: 45px;">
                                       <h4 style="font-size: 14px;text-align:left;line-height: 20px;">Текст текст текст </h4>
                                       <p style="line-height: 15px;">текст текст текст текст</p>
                                    </div>
                                 </div>
                                 <!-- green select row -->
                                 <div class="row chartselect1" id="chartselect1">
                                    <div class="col-xs-3" id="chartselect1round">
                                       <h2 style="margin: 5px auto;line-height: 35px;">1</h2>
                                    </div>
                                    <div class="col-xs-9" style="padding: 5px 10px;height: 45px;">
                                       <h4 style="font-size: 14px;text-align:left;line-height: 20px;">Текст текст текст </h4>
                                       <p style="line-height: 15px;">текст текст текст текст</p>
                                    </div>

                                 </div>
                              </div>
                           </div>
                  </div>
                  <!-- decription of barchart -->
                  <div class="row" style="height:40px;">
                       <div class="row" style="height:23px;">
                          <p style="font-size:12px;padding-left:10px;">Оценка времени образования зубного налета:</p>
                       </div>
                       <div class="row" style="padding:0 0 0 10px;">
                           <div class="col-xs-3" style="width:122.5px;">
                              <div class="col-xs-2" style="height:15px;width:10px;background:#9400d3;margin:0;padding:0;"></div>
                              <div class="col-xs-10" style="border-bottom:2px solid #9400d3;height:15px;width:112.5px;">
                                 <p style="line-height: 12px;margin-left: 5px;font-size:10px;">##% - месяц</p>
                              </div>
                           </div>
                           <div class="col-xs-3" style="width:122.5px;">
                              <div class="col-xs-2" style="height:15px;width:10px;background:#d342ff;margin:0;padding:0;"></div>
                              <div class="col-xs-10" style="border-bottom:2px solid #d342ff;height:15px;width:112.5px;">
                                 <p style="line-height: 12px;margin-left: 5px;font-size:10px;">##% - неделя</p>
                              </div>
                           </div>
                           <div class="col-xs-3" style="width:122.5px;">
                              <div class="col-xs-2" style="height:15px;width:10px;background:#ff99ff;margin:0;padding:0;"></div>
                              <div class="col-xs-10" style="border-bottom:2px solid #ff99ff;height:15px;width:112.5px;">
                                 <p style="line-height: 12px;margin-left: 5px;font-size:10px;">##% - сутки</p>
                              </div>
                           </div>
                           <div class="col-xs-3" style="width:122.5px;">
                              <div class="col-xs-2" style="height:15px;width:10px;background:#cccccc;margin:0;padding:0;"></div>
                              <div class="col-xs-10" style="border-bottom:2px solid #cccccc;height:15px;width:112.5px;">
                                 <p style="line-height: 12px;margin-left: 5px;font-size:10px;">##% - не обнаружен</p>
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
                           <div class="bar-under"><h5>ДД/ММ/ГГГГ</h5></div>

                        </div>
                        <div class="bar-inner" id="bar-inner"><h5>##%</h5></div>
                     </div>
                     <div class="col-xs-6" style="height:250px;width:230px;margin: 0;">
                        <h4 style="margin: 15px auto 10px;font-size:14px;">Группа риска №#</h4>
                        <p class="riskgroup_p">Текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст.</p>
                        <p class="riskgroup_p">Текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст.</p>
                        <p class="riskgroup_p">Текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст, текст</p>
                     </div>
                  </div>
                  <!-- upperlined text row -->
                  <div class="row row13">
                     <p>текст, текст, текст, текст, текст, текст, текст, текст, текст, текст</p>
                  </div>
            </div>
      <!-- right block -->
      <div class="col-xs-4 right_block">
                  <!-- first row with date/time -->
                  <div class="row right_block_1">
                     <h4>12.05.2020 / 12:34:56</h4>
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
                     <p>текст, текст, текст, текст, текст</p>
                  </div>
            </div>
   </div>
   <!--   ОСНОВНОЙ БЛОК   -->



<!--   забивка пространства   -->
   <div class="row footer">
      <div class="row footer__back" style="margin:20px auto;height:100px;width:100%;">
        <div class="col-xs-4">
            <h5>Переключатели</h5>
            <h5 id="selectors">3</h5>
        </div>
        <div class="col-xs-4">
           <h5>График 1</h5>
            <h5 id="chart_1_data_1">30</h5>
            <h5 id="chart_1_data_2">10</h5>
            <h5 id="chart_1_data_3">10</h5>
            <h5 id="chart_1_data_4">60</h5>
        </div>
        <div class="col-xs-4">
           <h5>График 2</h5>
            <h5 id="chart_2_data_1">30</h5>
            <h5 id="chart_2_data_2">20</h5>
            <h5 id="chart_2_data_3">10</h5>
        </div>


      </div>
   </div>
<!--   забивка пространства   -->


</body>
<!--   .JS, script & etc   -->
<?php require_once 'header/metafoot.php'; ?>
</html>
