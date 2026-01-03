package com.example.user.entity;

import com.fasterxml.jackson.annotation.JsonBackReference;


import jakarta.persistence.*;
import lombok.*;
import com.example.user.enums.Type;

@Entity
//@Data its not working
@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "participant_email")
public class Email {
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;

	private String email;

	@Enumerated(EnumType.STRING)
	private Type type; // Will be stored as "WORK", "HOME", etc.

	@ManyToOne
	@JoinColumn(name = "participant_id")
	@JsonBackReference
	private Participant participant;

	public Long getId() {
		return id;
	}

	public void setId(Long id) {
		this.id = id;
	}

	public String getEmail() {
		return email;
	}

	public void setEmail(String email) {
		this.email = email;
	}

	public Type getType() {
		return type;
	}

	public void setType(Type type) {
		this.type = type;
	}

	public Participant getParticipant() {
		return participant;
	}

	public void setParticipant(Participant participant) {
		this.participant = participant;
	}

}
