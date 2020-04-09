package org.zerock.controller;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.ServletException;
import java.io.IOException;


import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import lombok.extern.log4j.Log4j;

@Controller
@Log4j
public class CommonController {

	@GetMapping("/accessError")
	public void accessDenied(Authentication auth, Model model) {
		
		log.info("access Denied : " + auth);
		
		model.addAttribute("msg", "Access Denied");
	}
	
	@GetMapping("/customLogout")
	public void logoutGet(HttpServletRequest req, 
			HttpServletResponse res)
					throws ServletException, IOException {
		
		log.info("custom logout");
		res.sendRedirect("/login/login");
		
	}
	
	@GetMapping("/cctv_test")
	public String cctv_test(HttpServletRequest req, 
			HttpServletResponse res)
					throws ServletException, IOException {
		
		return "cctv_test";
		
	}
}
