package com.example.user.entity;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.example.user.enums.Type;
import jakarta.persistence.*;
import lombok.*;

@Entity
//@Data its not working
@Setter
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Table(name = "participant_phonenumber")
public class PhoneNumber {
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;

	private String number;

	@Enumerated(EnumType.STRING)
	private Type type; // Will be stored as "WORK", "HOME", etc.

	/*
	 * @Enumerated(EnumType.STRING) private PhoneType type = PhoneType.PERSONAL;
	 */
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

	public String getNumber() {
		return number;
	}

	public void setNumber(String number) {
		this.number = number;
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
