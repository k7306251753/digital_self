package com.example.user.reposetry;

import com.example.user.entity.Recognition;
import com.example.user.entity.Participant;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface RecognitionRepository extends JpaRepository<Recognition, Long> {
    List<Recognition> findByReceiver(Participant receiver);
}
