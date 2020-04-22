<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ page session="false" %>
<%@ page contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" language="java" %>
<html lang="en">
   <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link href="<c:url value="/resources/css/homeanimation.css"/>" rel="stylesheet">
    <link href="<c:url value="/resources/css/fullpage.min.css"/>" rel="stylesheet">
    <link href="<c:url value="/resources/css/homestyle.css"/>" rel="stylesheet">
    <link href="<c:url value="/resources/css/reset.css"/>" rel="stylesheet">
    <script 
        src="https://code.jquery.com/jquery-3.4.1.min.js"
        integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo="
        crossorigin="anonymous">
    </script>
</head>
<body>
    <!--헤더-->
    <header id="header">
        <div class="logo">
            <a href="#">
                <img src="resources/img/logo_w.png" alt="로고">
            </a>
            <a href="/login/login" class="login">로그인</a>
            <a href="#" class="join">회원가입</a>
        </div>
    </header> 
    <!--//헤더-->
    <!--fullpage 라이브러리-->
    <div id="full-page">
        <div class="section s0 section-two">
            <div class="slide img1 slide-one">
                <h2>Section 2</h2>
				<p>This is paragraph nr.1 in Section 2 / Slide 1</p>
				<p>This is paragraph nr.2 in Section 2 / Slide 1</p>
            </div>
            <div class="slide img2 slide-two">
                <h2>Section 2 </h2>
				<p>This is paragraph nr.1 in Section 2 / Slide 2</p>
				<p>This is paragraph nr.2 in Section 2 / Slide 2</p>
            </div>
            <div class="slide img3 slide-three">
                <h2>Section 2/h2>
				<p>This is paragraph nr.1 in Section 2 / Slide 3</p>
				<p>This is paragraph nr.2 in Section 2 / Slide 3</p>
            </div>
            <div class="slide img4 slide-four">
                <h2>Section 2</h2>
				<p>This is paragraph nr.1 in Section 2 / Slide 4</p>
				<p>This is paragraph nr.2 in Section 2 / Slide 4</p>
            </div>
        </div>
        <div class="section s1 section-one">
            <h2>Section 2</h2>
			<p>This is paragraph nr.1 in Section 2</p>
			<p>This is paragraph nr.2 in Section 2</p>
			<p>This is paragraph nr.3 in Section 2</p>
        </div>
        <div class="section s2 section-three">
            <h2>section 2</h2>
        </div>
        <div class="section s3 section-fore">
            <h2>section 3</h2>
        </div>
    </div>
    <script type="text/javascript"src="<c:url value="/resources/js/fullpage.min.js" />"></script>
    <!--//fullpage 라이브러리-->
    <script>
        new fullpage('#full-page', {
            //options here
            licenseKey: 'OPEN-SOURCE-GPLV3-LICENSE',
            autoScrolling:true,
            scrollHorizontally: true,
            navigation : true,
            navigationTooltips : ['home','about','contact','what'], //사이드 메뉴 이름 설정
            
            onLeave: function(origin, destination, direction){
                console.log("onLeave",origin.index, destination.index);
            },//스크롤이 시작할때 실행, origin:원래 있던 섹션 destination:가는 섹션
            afterLoad: function(origin, destination, direction){
                if(destination.index == 1){
                    $('.s1 h3').show();
                }
            },//스크롤이 끝날때 실행
        });

        //슬라이드 자동 재생
        $(document).ready(function () {
            $('#fullpage').fullpage({
                sectionsColor: ['#1bbc9b', '#4BBFC3'],
                loopBottom: true,
                afterRender: function () {
                    setInterval(function () {
                        $.fn.fullpage.moveSlideRight();
                    }, 500);
                }
            });
        });

    </script>
</body>
</html>