package com.example.user.entity;

import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonManagedReference;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;
import lombok.EqualsAndHashCode;

@Entity
@ToString(exclude = { "addresses", "phoneNumbers", "emails" })
@EqualsAndHashCode(exclude = { "addresses", "phoneNumbers", "emails" })
@Setter
@Getter
@Table(name = "participant")
public class Participant {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private long userId;

	private String userName;
	private String fullName;
	private String paxProfileImageUrl;
	private String password;
	private String department;
	private String userType;
	private long bankAccountNumber;
	private long points = 1000;

	@OneToMany(mappedBy = "participant", cascade = CascadeType.ALL)
	@com.fasterxml.jackson.annotation.JsonIgnore
	private List<Address> addresses = new ArrayList<>();

	@OneToMany(mappedBy = "participant", cascade = CascadeType.ALL)
	@com.fasterxml.jackson.annotation.JsonIgnore
	private List<PhoneNumber> phoneNumbers = new ArrayList<>();

	@OneToMany(mappedBy = "participant", cascade = CascadeType.ALL)
	@com.fasterxml.jackson.annotation.JsonIgnore
	private List<Email> emails = new ArrayList<>();

}
