-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 02, 2023 at 07:08 PM
-- Server version: 10.4.24-MariaDB
-- PHP Version: 7.4.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `perpspot_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `criminals`
--

CREATE TABLE `criminals` (
  `id` int(11) NOT NULL,
  `first_name` varchar(20) DEFAULT NULL,
  `last_name` varchar(20) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `nationality` varchar(20) DEFAULT NULL,
  `gender` varchar(6) DEFAULT NULL,
  `phone_number` int(9) DEFAULT NULL,
  `height` float DEFAULT NULL,
  `weight` float DEFAULT NULL,
  `crime_category` varchar(15) DEFAULT NULL,
  `crime_type` varchar(15) DEFAULT NULL,
  `date_of_offense` date DEFAULT NULL,
  `location_of_offense` varchar(25) DEFAULT NULL,
  `perp_image_path` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `criminals`
--

INSERT INTO `criminals` (`id`, `first_name`, `last_name`, `birth_date`, `nationality`, `gender`, `phone_number`, `height`, `weight`, `crime_category`, `crime_type`, `date_of_offense`, `location_of_offense`, `perp_image_path`) VALUES
(1, 'Mike', 'Hunt', '2009-04-30', 'Ghanaian', 'Male', 248754879, 185, 73, 'Drugs', 'Drug Possession', '2023-03-15', 'Pokuase', 'static/faces/Mike_Hunt/Mike_Hunt_0.jpg'),
(3, 'Mike', 'Hunt', '2001-04-05', 'Ghanaian', 'Male', 208457856, 158, 75, 'Violent', 'Assault', '2023-02-08', 'Ho', 'static/faces/Mike_Hunt/Mike_Hunt_0.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `identified`
--

CREATE TABLE `identified` (
  `id` int(3) NOT NULL,
  `date` date NOT NULL,
  `first_name` varchar(20) NOT NULL,
  `last_name` varchar(20) NOT NULL,
  `location` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `login_logout`
--

CREATE TABLE `login_logout` (
  `staffid` varchar(20) NOT NULL,
  `login_time` datetime NOT NULL,
  `logout_time` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `login_logout`
--

INSERT INTO `login_logout` (`staffid`, `login_time`, `logout_time`) VALUES
('GPPSA00001', '2023-03-19 01:59:21', '0000-00-00 00:00:00'),
('GPPSA00001', '2023-03-19 15:48:07', '0000-00-00 00:00:00'),
('GPPSA00001', '2023-03-19 20:56:18', '2023-03-19 20:56:24'),
('GPPSA00001', '2023-03-19 21:52:58', '2023-03-19 23:19:26'),
('GPPSA00001', '2023-03-20 16:50:33', '2023-03-20 16:51:15'),
('GPPSA00001', '2023-03-20 20:03:18', '0000-00-00 00:00:00'),
('GPPSA00001', '2023-03-20 21:33:09', '2023-03-20 23:23:55'),
('GPPSA00001', '2023-03-21 00:05:29', '0000-00-00 00:00:00'),
('GPPSA00001', '2023-03-21 00:06:15', '0000-00-00 00:00:00'),
('GPPSA00001', '2023-03-27 01:09:20', '2023-03-27 01:12:55'),
('GPPSA00001', '2023-03-31 15:33:11', '2023-03-31 15:35:28'),
('GPPSA00001', '2023-03-31 19:46:36', '2023-03-31 19:50:37'),
('GPPSA00001', '2023-04-01 14:55:58', '0000-00-00 00:00:00'),
('GPPSA00001', '2023-04-01 17:06:04', '2023-04-01 17:07:40'),
('GPPSA00001', '2023-04-01 17:52:31', '0000-00-00 00:00:00'),
('GPPSA00001', '2023-04-02 12:59:10', '0000-00-00 00:00:00'),
('GPPSA00001', '2023-04-02 14:03:08', '0000-00-00 00:00:00'),
('GPPSA00001', '2023-04-02 14:51:36', '0000-00-00 00:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `tips`
--

CREATE TABLE `tips` (
  `id` int(5) NOT NULL,
  `full_name` varchar(60) NOT NULL,
  `email` varchar(60) NOT NULL,
  `phone` varchar(60) NOT NULL,
  `category` varchar(30) NOT NULL,
  `message` text NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `tips`
--

INSERT INTO `tips` (`id`, `full_name`, `email`, `phone`, `category`, `message`, `timestamp`) VALUES
(1, 'Kofi Nti', 'knti@gmail.com', '590033452', 'Assault', 'Hello!', '2023-03-17 22:23:35'),
(2, 'Kofi Bonsu', 'kbonsu4@gmail.com', '558457458', 'Drug Offense', 'I saw someone with cocaine.', '2023-03-26 23:07:31');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(2) NOT NULL,
  `staff_id` varchar(10) NOT NULL,
  `password` varchar(300) NOT NULL,
  `role` int(1) NOT NULL,
  `last_login` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `staff_id`, `password`, `role`, `last_login`) VALUES
(1, 'kwartey', '12345', 1, '2023-03-02 16:41:52'),
(2, 'GPPSA00001', 'admin123', 1, '2023-03-16 13:29:23');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `criminals`
--
ALTER TABLE `criminals`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `identified`
--
ALTER TABLE `identified`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `login_logout`
--
ALTER TABLE `login_logout`
  ADD PRIMARY KEY (`staffid`,`login_time`);

--
-- Indexes for table `tips`
--
ALTER TABLE `tips`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `criminals`
--
ALTER TABLE `criminals`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `identified`
--
ALTER TABLE `identified`
  MODIFY `id` int(3) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tips`
--
ALTER TABLE `tips`
  MODIFY `id` int(5) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(2) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
