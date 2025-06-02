-- phpMyAdmin SQL Dump
-- version 5.0.4deb2+deb11u1
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jul 18, 2024 at 10:07 PM
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
-- Database: `synapsis_project`
--

-- --------------------------------------------------------

--
-- Table structure for table `connexSettingDB`
--

CREATE TABLE `connexSettingDB` (
  `id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL,
  `value` varchar(2) NOT NULL,
  `updatedAt` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `connexSettingDB`
--

INSERT INTO `connexSettingDB` (`id`, `name`, `value`, `updatedAt`) VALUES
(1, 'routineMonitor', '0', '2024-07-18 22:07:02'),
(2, 'bufferMonitor', '0', '2024-07-16 12:24:37'),
(3, 'bufferMonitorInterval', '10', '2024-07-08 15:25:54'),
(4, 'bufferMonitorUnit', '1', '2024-06-06 07:31:26'),
(5, 'alarmMonitor', '0', '2024-07-16 12:30:07'),
(6, 'alarmMonitorInterval', '10', '2024-07-08 15:25:54'),
(7, 'alarmMonitorUnit', '1', '2024-06-05 11:41:43'),
(8, 'notification', '0', '2024-07-16 12:24:58'),
(9, 'notificationInterval', '10', '2024-06-11 13:43:39'),
(10, 'notificationUnit', '1', '2024-06-11 13:43:39'),
(11, 'notificationSensorWeb', '1', '2024-04-23 16:25:04'),
(12, 'notificationSensorWA', '1', '2024-06-03 09:53:42'),
(13, 'notificationSensorEmail', '1', '2024-04-23 11:30:34'),
(14, 'notificationSensorTelegram', '1', '2024-06-03 09:53:42'),
(15, 'notificationActuatorWeb', '1', '2024-05-26 17:45:45'),
(16, 'notificationActuatorWA', '1', '2024-06-16 11:19:08'),
(17, 'notificationActuatorEmail', '1', '2024-06-16 11:19:08'),
(18, 'notificationActuatorTelegram', '1', '2024-04-23 16:25:04'),
(19, 'notificationNodeWeb', '1', '2024-04-23 11:30:34'),
(20, 'notificationNodeWA', '1', '2024-04-23 16:25:04'),
(21, 'notificationNodeEmail', '1', '2024-06-03 09:53:42'),
(22, 'notificationNodeTelegram', '1', '2024-04-23 11:30:34'),
(23, 'synchronize', '0', '2024-07-18 22:07:07'),
(24, 'synchronizeInterval', '5', '2024-06-03 14:00:56'),
(25, 'synchronizeUnit', '1', '2024-04-23 16:32:41'),
(26, 'syncSensor', '1', '2024-06-11 11:45:57'),
(27, 'syncActuator', '1', '2024-04-23 16:32:47'),
(28, 'syncNode', '1', '2024-06-04 13:43:29'),
(29, 'log', '0', '2024-07-16 12:25:05'),
(30, 'logInterval', '0', '2024-03-25 14:13:15'),
(31, 'logUnit', '0', '2024-03-25 14:13:15');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `connexSettingDB`
--
ALTER TABLE `connexSettingDB`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `connexSettingDB`
--
ALTER TABLE `connexSettingDB`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=32;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
