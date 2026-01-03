package com.example.user.service;

import com.example.user.entity.CommLog;
import com.example.user.reposetry.CommLogRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class CommLogService {

    @Autowired
    private CommLogRepository commLogRepository;

    public void logMessage(Long userId, String userName, String role, String content) {
        CommLog log = new CommLog();
        log.setUserId(userId);
        log.setUserName(userName);
        log.setRole(role);
        log.setContent(content);
        commLogRepository.save(log);
    }
}
