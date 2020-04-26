<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Push</title>

<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
<link rel="stylesheet" href="https://code.getmdl.io/1.2.1/material.indigo-pink.min.css">
<script defer src="https://code.getmdl.io/1.2.1/material.min.js"></script>
<script src="https://code.jquery.com/jquery-3.4.1.min.js" integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo=" crossorigin="anonymous"></script>
<link rel="stylesheet" href="/resources/css/pushtest.css">
</head>
<body>
	<header>	
		<h1>WebPush Notification</h1>
	</header>

	<main>
		<p>Welcome to the webpush notification. The button below needs to be
			fixed to support subscribing to push.</p>
		<p>
			<button disabled class="js-push-btn mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect">
				Enable Push Messaging
			</button>
		</p>
		<section class="subscription-details js-subscription-details is-invisible">
			<p>Once you've subscribed your user, you'd send their subscription to your
				server to store in a database so that when you want to send a message
				you can lookup the subscription and send a message to it.</p>
			<pre><code class="js-subscription-json"></code></pre>

			<hr>
			<p>You can test push notification below.</p>
			<button type="submit" class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" onclick="push_message()">Test Push Notification</button>
		</section>
	</main>

<%-- 	<script type="text/javascript"src="<c:url value="/resources/js/pushtest.js" />"></script> --%>
	<script type="text/javascript"src="/resources/js/pushtest.js"></script>
	<script src="https://code.getmdl.io/1.2.1/material.min.js"></script>
</body>
</html>