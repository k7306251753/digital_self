package com.example.user.reposetry;

import com.example.user.entity.CommLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CommLogRepository extends JpaRepository<CommLog, Long> {
}
