package com.example.user.reposetry;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.example.user.entity.Participant;
@Repository
public interface PaxReposetry extends JpaRepository<Participant, Long> {
	
@Query("select pax from Participant pax where pax.userName = :username")
	public Participant getByUserName(@Param("username") String username);

}
