-- phpMyAdmin SQL Dump
-- version 5.0.4deb2+deb11u1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jul 15, 2024 at 09:21 AM
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
-- Table structure for table `interface`
--

CREATE TABLE `interface` (
  `name` varchar(10) NOT NULL,
  `tipe` tinyint(1) NOT NULL,
  `conn` tinyint(1) DEFAULT NULL,
  `mac` varchar(30) DEFAULT NULL,
  `ip` varchar(30) DEFAULT NULL,
  `subnet` varchar(30) DEFAULT NULL,
  `gateway` varchar(30) DEFAULT NULL,
  `dns` varchar(30) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `interface`
--

INSERT INTO `interface` (`name`, `tipe`, `conn`, `mac`, `ip`, `subnet`, `gateway`, `dns`) VALUES
('eth0', 0, 0, 'd8:3a:dd:04:b9:3a', '192.168.1.10', '255.255.255.0', '192.168.1.1', '8.8.8.8'),
('wlan0', 1, 0, 'b8:27:eb:22:c3:97', '172.16.11.1', '255.255.255.0', '', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `interface`
--
ALTER TABLE `interface`
  ADD PRIMARY KEY (`name`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
