-- phpMyAdmin SQL Dump
-- version 5.0.4deb2+deb11u1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jul 15, 2024 at 09:20 AM
-- Server version: 10.5.23-MariaDB-0+deb11u1
-- PHP Version: 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `synapsis_control`
--

-- --------------------------------------------------------

--
-- Table structure for table `wireless`
--

CREATE TABLE `wireless` (
  `name` varchar(10) NOT NULL,
  `interface` varchar(10) NOT NULL,
  `state` tinyint(1) NOT NULL,
  `ssid` varchar(30) NOT NULL,
  `password` varchar(30) NOT NULL,
  `channel` tinyint(2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `wireless`
--

INSERT INTO `wireless` (`name`, `interface`, `state`, `ssid`, `password`, `channel`) VALUES
('hotspot', 'wlan0', 1, 'Nearon DCM v1.0.0', '12345678', 1),
('station', '', 0, '', '', 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `wireless`
--
ALTER TABLE `wireless`
  ADD PRIMARY KEY (`name`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
