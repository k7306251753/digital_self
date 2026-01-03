package com.example.user.contoller;

import com.example.user.service.CommLogService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/empengagement/comm-log")
@CrossOrigin(origins = "*")
public class CommLogController {

    @Autowired
    private CommLogService commLogService;

    @PostMapping
    public ResponseEntity<Void> logMessage(@RequestBody Map<String, Object> payload) {
        Long userId = payload.get("userId") != null ? Long.valueOf(payload.get("userId").toString()) : null;
        String userName = (String) payload.get("userName");
        String role = (String) payload.get("role");
        String content = (String) payload.get("content");

        commLogService.logMessage(userId, userName, role, content);
        return ResponseEntity.ok().build();
    }
}
